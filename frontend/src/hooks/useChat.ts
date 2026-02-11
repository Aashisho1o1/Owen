import { useState, useEffect, useCallback, useRef } from 'react';
import { sendChatMessage, buildChatRequest, generateSuggestions } from '../services/api/chat';
import { useAuth } from '../contexts/AuthContext';
import { useApiHealth } from './useApiHealth';
import api, { ChatMessage, ChatRequest, ChatResponse, UserPreferences } from '../services/api';
import { logger } from '../utils/logger';

interface ApiErrorData {
  error?: string;
  detail?: string | Array<{ loc: string[]; msg: string; type: string }>;
  [key: string]: unknown;
}

interface ApiError {
  message: string;
  response?: {
    status: number;
    statusText: string;
    data?: ApiErrorData;
  };
  request?: unknown;
}

export interface UseChatOptions {
  initialMessages?: ChatMessage[];
  authorPersona: string;
  helpFocus: string;
  editorContent: string;
  selectedLLM: string;
  aiMode: string;
  folderScopeEnabled?: boolean; // Premium Feature 1
  voiceGuardEnabled?: boolean; // Premium Feature 2
  setApiGlobalError?: React.Dispatch<React.SetStateAction<string | null>>;
  userPreferences?: UserPreferences;
  feedbackOnPrevious?: string;
  highlightedText?: string;
  highlightedTextId?: string;
  onAuthRequired?: () => void;
  setHighlightedTextMessageIndex?: React.Dispatch<React.SetStateAction<number | null>>;
}

export interface UseChatReturn {
  messages: ChatMessage[];
  setMessages: React.Dispatch<React.SetStateAction<ChatMessage[]>>;
  thinkingTrail: string | null;
  apiError: string | null;
  setApiError: React.Dispatch<React.SetStateAction<string | null>>;
  isStreaming: boolean;
  streamText: string;
  isThinking: boolean;
  handleSendMessage: (message: string) => Promise<void>;
  handleSaveCheckpoint: () => Promise<void>;
  fullResponse: string; 
}

// Configuration for the chat API - MUST be defined in .env file
const chatApiUrl = import.meta.env.VITE_API_URL;
if (!chatApiUrl) {
  console.error('❌ CRITICAL: VITE_API_URL is not defined in useChat hook');
  throw new Error('VITE_API_URL environment variable is required but not defined');
}

const CHAT_CONFIG = {
  apiUrl: chatApiUrl,
  endpoints: {
    chat: '/api/chat/stream',
    suggestions: '/api/chat/suggestions',
  }
};

export const useChat = ({
  initialMessages = [],
  authorPersona,
  helpFocus,
  editorContent,
  selectedLLM,
  aiMode,
  folderScopeEnabled = false, // Default to false for cost control
  voiceGuardEnabled = false, // Default to false for cost control
  setApiGlobalError,
  userPreferences,
  feedbackOnPrevious,
  highlightedText,
  highlightedTextId,
  onAuthRequired,
  setHighlightedTextMessageIndex,
}: UseChatOptions): UseChatReturn => {
  // Core chat state
  const [messages, setMessages] = useState<ChatMessage[]>(initialMessages);
  const [thinkingTrail, setThinkingTrail] = useState<string | null>(null);
  const [apiError, setApiError] = useState<string | null>(null);
  const [isStreaming, setIsStreaming] = useState(false);
  const [streamText, setStreamText] = useState('');
  const [streamIndex, setStreamIndex] = useState(0);
  const [isThinking, setIsThinking] = useState(false);
  const [fullResponse, setFullResponse] = useState('');
  
  // Request management to prevent stale responses
  const currentRequestId = useRef<number>(0);
  const lastHighlightTextRef = useRef<string | null>(null);

  // Auto-set initial welcome message when persona changes
  useEffect(() => {
    // Only update if we don't have messages or need to refresh persona
    if (authorPersona && helpFocus) {
      // Create a personalized welcome message based on user preferences
      const englishVariantLabel = userPreferences?.english_variant === 'indian' ? 'Indian English' :
                                 userPreferences?.english_variant === 'british' ? 'British English' :
                                 userPreferences?.english_variant === 'american' ? 'American English' : '';
      
      const variantText = englishVariantLabel ? ` I'll respect your ${englishVariantLabel} preferences.` : '';
      
      const welcomeMessage = {
        role: 'assistant' as const,
        content: `Hello, I'm your ${authorPersona} AI writing assistant. I'll help you with your ${helpFocus.toLowerCase()}.${variantText} What would you like to ask?`,
      };

      // If there are no messages, create the initial welcome message
      if (messages.length === 0) {
        setMessages([welcomeMessage]);
      } else {
        // If there are messages and the first one is a welcome message, update it
        const firstMessage = messages[0];
        if (firstMessage?.role === 'assistant' && firstMessage.content.includes('AI writing assistant')) {
          setMessages(prev => [welcomeMessage, ...prev.slice(1)]);
        }
      }
      
      setThinkingTrail(null); // Reset thinking trail with persona change
    }
  }, [authorPersona, helpFocus, initialMessages.length, userPreferences?.english_variant]);
  
  // Effect for simulating typing stream - OPTIMIZED FOR PERFORMANCE
  useEffect(() => {
    if (!isStreaming || streamIndex >= fullResponse.length) {
      if (isStreaming && streamIndex >= fullResponse.length) {
        // Streaming complete - clean up
        setIsStreaming(false);
        setStreamText('');
        setStreamIndex(0);
      }
      return;
    }

    // Use requestAnimationFrame for smoother, synchronized updates
    const frameId = requestAnimationFrame(() => {
      // Batch multiple characters for smoother animation (reduces DOM thrashing)
      const charsToAdd = Math.min(3, fullResponse.length - streamIndex);
      const newText = fullResponse.substring(0, streamIndex + charsToAdd);
      setStreamText(newText);
      setStreamIndex(prevIndex => prevIndex + charsToAdd);
    });

    return () => cancelAnimationFrame(frameId);
  }, [isStreaming, streamIndex, fullResponse]);


  const handleSendMessage = useCallback(async (message: string) => {
    if (!message.trim()) return;
    
    // If already streaming, cancel the previous request
    if (isStreaming) {
      console.log('🔄 New message while streaming - canceling previous request');
      currentRequestId.current += 1; // Invalidate previous request
      setIsStreaming(false);
      setStreamText('');
      setStreamIndex(0);
    }
    
    // Capture current request ID for this specific request
    const requestId = currentRequestId.current;
    
    setIsStreaming(true);
    setIsThinking(true);
    setThinkingTrail('');
    setApiError(null);
    
    // Determine whether this highlighted text has already been used
    const isFirstHighlightUse = highlightedText && highlightedText.trim() && highlightedText !== lastHighlightTextRef.current;

    const userMessage: ChatMessage = {
      role: 'user',
      content: message,
      // Only preserve highlight on the first message after a selection
      ...(isFirstHighlightUse && highlightedText?.trim()
        ? { highlightedText, highlightedTextId }
        : {}),
    } as ChatMessage;
    
    // Add user message immediately - this won't be affected by request cancellation
    setMessages(prev => {
      const newMessages = [...prev, userMessage];
      
      // Associate the highlight with ONLY the first related message
      if (isFirstHighlightUse && setHighlightedTextMessageIndex) {
        setHighlightedTextMessageIndex(newMessages.length - 1);
        // Remember that we've now consumed this highlight
        lastHighlightTextRef.current = highlightedText || null;
      }
      
      return newMessages;
    });
    
    try {
      logger.info('📤 Sending chat request:', {
        requestId,
        messageLength: message.length,
        editorContentLength: editorContent.length,
        authorPersona,
        helpFocus,
        selectedLLM,
        hasHighlightedText: !!highlightedText,
        aiMode,
        folderScopeEnabled,
        voiceGuardEnabled
      });
      
      const requestPayload = {
        message,
        editor_text: editorContent, // Use original content
        author_persona: authorPersona,
        help_focus: helpFocus,
        chat_history: [...messages, userMessage],
        llm_provider: selectedLLM,
        user_preferences: userPreferences || {
          onboarding_completed: false,
          user_corrections: []
        },
        feedback_on_previous: feedbackOnPrevious || "",
        // Send highlight context to the backend only the first time
        highlighted_text: isFirstHighlightUse ? highlightedText || "" : "",
        highlight_id: isFirstHighlightUse ? highlightedTextId || "" : "",
        english_variant: "US",
        ai_mode: aiMode,
        // Premium Features (opt-in)
        voice_guard: voiceGuardEnabled
      };
      
      // CRITICAL FIX: Use suggestions endpoint for Co-Edit mode with highlighted text
      const shouldUseSuggestions = aiMode === 'co-edit' && highlightedText && highlightedText.trim().length > 0;
      
      let response;
      if (shouldUseSuggestions) {
        logger.info('🎯 Using suggestions endpoint for Co-Edit mode with highlighted text');
        const suggestionsResponse = await generateSuggestions(requestPayload);
        
        // Convert suggestions response to regular chat response format
        response = {
          dialogue_response: suggestionsResponse.dialogue_response,
          thinking_trail: suggestionsResponse.thinking_trail,
          // Store suggestions in a special property that will be handled by ChatContext
          suggestions: suggestionsResponse.suggestions,
          has_suggestions: suggestionsResponse.has_suggestions,
          original_text: suggestionsResponse.original_text
        };
        
        logger.info(`✨ Generated ${suggestionsResponse.suggestions?.length || 0} suggestions automatically`);
      } else {
        logger.info('💬 Using regular chat endpoint');
        response = await api.sendChatMessage(requestPayload);
      }

      // Check if this request is still valid (user hasn't sent a new message)
      if (requestId !== currentRequestId.current) {
        console.log('🚫 Request cancelled - newer request in progress', { 
          currentRequestId: currentRequestId.current, 
          thisRequestId: requestId 
        });
        return; // Silently abandon this response
      }

      console.log('📥 Received chat response:', response);
      
      setIsThinking(false);
      
      if (response && response.dialogue_response && response.dialogue_response.trim()) {
        const finalResponse = response.dialogue_response;
        
        // Create placeholder assistant message immediately
        const assistantMessage: ChatMessage = {
          role: 'assistant',
          content: '', // Start empty for streaming effect
          timestamp: new Date(),
        };
        
        // Add placeholder message and remember its index
        let assistantMessageIndex = -1;
        setMessages(prev => {
          const newMessages = [...prev, assistantMessage];
          assistantMessageIndex = newMessages.length - 1;
          return newMessages;
        });
        
        setFullResponse(finalResponse);
        setIsStreaming(true); // Start streaming the response
        setStreamIndex(0); // Reset stream index
        setThinkingTrail(response.thinking_trail || null);
        
        // SIMPLIFIED: Update the placeholder message using the existing useEffect streaming
        // The useEffect above handles the progressive updates
        const updatePlaceholderMessage = (content: string) => {
          setMessages(prev => prev.map((msg, index) => 
            index === assistantMessageIndex 
              ? { ...msg, content } 
              : msg
          ));
        };
        
        // Watch for streamText changes and update the message content
        const updateInterval = setInterval(() => {
          if (requestId !== currentRequestId.current) {
            clearInterval(updateInterval);
            return;
          }
          
          // Get current stream text and update the message
          setMessages(prev => prev.map((msg, index) => 
            index === assistantMessageIndex 
              ? { ...msg, content: streamText } 
              : msg
          ));
          
          // Check if streaming is complete
          if (!isStreaming) {
            clearInterval(updateInterval);
            // Final update with complete message
            setMessages(prev => prev.map((msg, index) => 
              index === assistantMessageIndex 
                ? { ...msg, content: finalResponse } 
                : msg
            ));
          }
        }, 100); // Reduced frequency to prevent blinking
        
        // CRITICAL: Dispatch suggestions to ChatContext if available
        if (response.suggestions && response.has_suggestions) {
          // Dispatch custom event to notify ChatContext about suggestions
          window.dispatchEvent(new CustomEvent('suggestionsGenerated', {
            detail: {
              suggestions: response.suggestions,
              originalText: response.original_text || highlightedText,
              dialogueResponse: response.dialogue_response
            }
          }));
        }
      } else {
        // Handle cases where dialogue_response might be empty or undefined
        console.warn('⚠️ Empty or invalid response received:', response);
        const fallbackMessage = `I apologize, but I received an empty response. As ${authorPersona} would say, let's try again with a different approach.`;
        setMessages(prev => [
          ...prev,
          { role: 'assistant', content: fallbackMessage }
        ]);
        setThinkingTrail('Empty response received - using fallback');
        setIsStreaming(false);
      }

    } catch (error: unknown) {
      // Check if request is still valid before handling error
      if (requestId !== currentRequestId.current) {
        console.log('🚫 Error handling cancelled - newer request in progress');
        return;
      }
      
      logger.error('❌ Error sending message in useChat:', error);
      setIsThinking(false);
      setIsStreaming(false);
      
      const typedError = error as ApiError & { userMessage?: string; isAuthError?: boolean; isNetworkError?: boolean; debugInfo?: string };
      
      // Enhanced error logging for debugging
      console.error('🔍 Detailed error analysis:', {
        errorMessage: typedError.message,
        errorName: typedError.name,
        errorStack: typedError.stack,
        hasResponse: !!typedError.response,
        responseStatus: typedError.response?.status,
        responseData: typedError.response?.data,
        hasRequest: !!typedError.request,
        userMessage: typedError.userMessage,
        isAuthError: typedError.isAuthError,
        isNetworkError: typedError.isNetworkError,
        debugInfo: typedError.debugInfo,
        apiUrl: CHAT_CONFIG.apiUrl,
        timestamp: new Date().toISOString()
      });
      
      // CRITICAL FIX: Check if this is an enhanced error from API client first
      if (typedError.message && (
        typedError.message.includes('🔐 Authentication required') ||
        typedError.message.includes('🌐 Network error') ||
        typedError.message.includes('⏱️ Request timeout') ||
        typedError.message.includes('🔧 Server error')
      )) {
        // This is an enhanced error from the API client - use it directly
        console.log('✅ Using enhanced error message from API client:', typedError.message);
        
        // Add the enhanced error message as an assistant response
        setMessages(prev => [
          ...prev,
          { role: 'assistant', content: typedError.message }
        ]);
        
        // Set the error for the error display component
        setApiError(typedError.message);
        setThinkingTrail(`Enhanced error: ${typedError.debugInfo || typedError.message}`);
        
        // Set global error only for network issues (not auth issues)
        if (setApiGlobalError && typedError.isNetworkError) {
          setApiGlobalError(typedError.message);
        }
        
        return; // Exit early - we've handled the enhanced error
      }
      
      // Fallback to legacy error handling for non-enhanced errors
      console.log('⚠️ Using legacy error handling for non-enhanced error');
      
      // Create a user-friendly fallback response based on the error type
      let fallbackResponse = '';
      let errorType = 'unknown';
      
      if (typedError.message?.includes('timeout') || typedError.message?.includes('Request timeout')) {
        errorType = 'timeout';
        fallbackResponse = `I apologize, but my response took too long (over 60 seconds). As ${authorPersona} would say, sometimes the best writing comes from patience. Please try your question again, perhaps with fewer details.`;
      } else if (typedError.message?.includes('Network Error') || typedError.message?.includes('ECONNREFUSED')) {
        errorType = 'network';
        fallbackResponse = `I'm having trouble connecting to the writing assistant service. As ${authorPersona} would say, even the best writers face technical obstacles. Please check your internet connection and try again.`;
      } else if (typedError.response?.status === 500) {
        errorType = 'server';
        fallbackResponse = `I encountered a server issue while processing your request. As ${authorPersona} would say, every writer faces technical difficulties. Let me try to help you differently - could you rephrase your question?`;
      } else if (typedError.response?.status === 429) {
        errorType = 'rate_limit';
        fallbackResponse = `I'm receiving too many requests right now. As ${authorPersona} would say, good writing takes time. Please wait a moment and try again.`;
      } else if (typedError.response?.status === 400) {
        errorType = 'bad_request';
        
        // Check if this is a token limit error
        const errorDetail = typedError.response?.data?.detail || '';
        if (errorDetail.includes('Input too long') || errorDetail.includes('too long')) {
          errorType = 'token_limit';
          fallbackResponse = `📝 Your document is too long for AI processing. The system supports documents up to 100,000 characters. Please try reducing the length of your document or break it into smaller sections.`;
        } else {
          fallbackResponse = `There was an issue with your request format. As ${authorPersona} would say, clarity is key in both writing and communication. Please try rephrasing your question.`;
        }
      } else if (typedError.response?.status === 403 || typedError.response?.status === 401) {
        errorType = 'auth';
        fallbackResponse = `🔐 Authentication Required: You need to be signed in to use the AI Writing Assistant. Please sign in or create an account to start getting personalized writing feedback from ${authorPersona}.`;
      } else {
        errorType = 'general';
        fallbackResponse = `I encountered an unexpected issue: ${typedError.message || 'Unknown error'}. As ${authorPersona} would say, every writer faces challenges. Please try rephrasing your question or ask something else.`;
      }
      
      // Add the fallback response to chat
      setMessages(prev => [
        ...prev,
        { role: 'assistant', content: fallbackResponse }
      ]);
      
      // Set detailed error for debugging (but don't show to user)
      let specificApiError = `Error (${errorType}): ${typedError.message || 'Unknown error'}`;
      if (typedError.response && typedError.response.data) {
        const errorDetail = typedError.response.data.detail || typedError.response.data.error || JSON.stringify(typedError.response.data);
        specificApiError = `API error (${errorType}): ${typedError.response.status} - ${errorDetail}`;
      } else if (typedError.response) {
        specificApiError = `API error (${errorType}): ${typedError.response.status} - ${typedError.response.statusText}`;
      }
      
      setApiError(specificApiError);
      setThinkingTrail(`Error occurred: ${errorType} - ${specificApiError}`);
      
      // Set global error only for critical connection-related issues
      // Don't set global error for auth issues if they happen right after login
      if (setApiGlobalError && (errorType === 'network' || errorType === 'timeout')) {
        setApiGlobalError(`Backend connection issue (${errorType}). Backend URL: ${CHAT_CONFIG.apiUrl}. Please check if the server is running.`);
      }
    }
  }, [messages, editorContent, authorPersona, helpFocus, selectedLLM, userPreferences, feedbackOnPrevious, highlightedText, highlightedTextId, aiMode, isStreaming]);

  const handleSaveCheckpoint = useCallback(async () => {
    logger.log("Save Checkpoint clicked");
    try {
      await api.saveCheckpoint({ editor_text: editorContent, chat_history: messages });
      logger.log("Checkpoint saved successfully.");
    } catch (error) {
      const typedError = error as ApiError;
      let specificApiError = `Error saving checkpoint: ${typedError.message || 'Unknown error'}`;
      if (typedError.response && typedError.response.data) {
        const errorDetail = typedError.response.data.detail || typedError.response.data.error || JSON.stringify(typedError.response.data);
        specificApiError = `Checkpoint API error: ${typedError.response.status} - ${errorDetail}`;
      } else if (typedError.response) {
        specificApiError = `Checkpoint API error: ${typedError.response.status} - ${typedError.response.statusText}`;
      }
      
      // Use global error setter if provided, otherwise use local error state
      if (setApiGlobalError) {
        setApiGlobalError(specificApiError);
      } else {
        setApiError(specificApiError);
      }
    }
  }, [editorContent, messages, setApiGlobalError]);

  return {
    messages,
    setMessages, // Expose setMessages if direct manipulation is needed (e.g., for clearing chat)
    thinkingTrail,
    apiError,
    setApiError, // Allow parent to clear API error if needed
    isStreaming,
    streamText,
    isThinking,
    handleSendMessage,
    handleSaveCheckpoint,
    fullResponse,
  };
  };
