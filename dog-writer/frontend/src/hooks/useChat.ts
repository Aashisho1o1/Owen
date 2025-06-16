import { useState, useEffect, useCallback } from 'react';
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
  setApiGlobalError?: React.Dispatch<React.SetStateAction<string | null>>;
  userPreferences?: UserPreferences;
  feedbackOnPrevious?: string;
  highlightedText?: string;
  highlightedTextId?: string;
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

export const useChat = ({
  initialMessages = [],
  authorPersona,
  helpFocus,
  editorContent,
  selectedLLM,
  setApiGlobalError,
  userPreferences,
  feedbackOnPrevious,
  highlightedText,
  highlightedTextId,
}: UseChatOptions): UseChatReturn => {
  const [messages, setMessages] = useState<ChatMessage[]>(initialMessages);
  const [thinkingTrail, setThinkingTrail] = useState<string | null>(null);
  const [apiError, setApiError] = useState<string | null>(null);
  const [isStreaming, setIsStreaming] = useState(false);
  const [streamText, setStreamText] = useState('');
  const [streamIndex, setStreamIndex] = useState(0);
  const [fullResponse, setFullResponse] = useState('');
  const [isThinking, setIsThinking] = useState(false);

  useEffect(() => {
    // Initialize with a welcome message if no initial messages are provided
    // and ensure messages isn't empty to prevent re-triggering.
    if (initialMessages.length === 0 && messages.length === 0) {
      const englishVariantLabel = userPreferences?.english_variant === 'indian' ? 'Indian English' :
                                 userPreferences?.english_variant === 'british' ? 'British English' :
                                 userPreferences?.english_variant === 'american' ? 'American English' : '';
      
      const variantText = englishVariantLabel ? ` I'll respect your ${englishVariantLabel} preferences.` : '';
      
      setMessages([
        {
          role: 'assistant',
          content: `Hello, I'm your ${authorPersona} AI writing assistant. I'll help you with your ${helpFocus.toLowerCase()}.${variantText} What would you like to ask?`,
        },
      ]);
      setThinkingTrail(null); // Reset thinking trail with persona change
    }
  }, [authorPersona, helpFocus, initialMessages.length, messages.length, userPreferences?.english_variant]);
  
  // Effect for simulating typing stream
  useEffect(() => {
    if (!isStreaming || streamIndex >= fullResponse.length) {
      if (isStreaming && streamIndex >= fullResponse.length) {
        // Add the complete streamed message to chat history
        setMessages(prev => [
          ...prev,
          { role: 'assistant' as const, content: fullResponse }
        ]);
        setIsStreaming(false); // End streaming
      }
      return;
    }

    const typingSpeed = Math.random() * 30 + 20; // Simulate variable typing speed
    const timer = setTimeout(() => {
      setStreamText(fullResponse.substring(0, streamIndex + 1));
      setStreamIndex(prevIndex => prevIndex + 1);
    }, typingSpeed);

    return () => clearTimeout(timer);
  }, [isStreaming, streamIndex, fullResponse]);


  const handleSendMessage = useCallback(async (message: string) => {
    const newUserMessage: ChatMessage = { role: 'user', content: message };
    const updatedMessages = [...messages, newUserMessage];
    setMessages(updatedMessages);
    
    setApiError(null);
    setIsStreaming(false);
    setStreamText('');
    setStreamIndex(0);
    setIsThinking(true);
    setThinkingTrail(null); // Clear previous thinking trail

    try {
      const requestData: ChatRequest = {
        message,
        editor_text: editorContent,
        author_persona: authorPersona,
        help_focus: helpFocus,
        chat_history: updatedMessages, // Send the latest messages including the current user message
        llm_provider: selectedLLM,
        user_preferences: userPreferences,
        feedback_on_previous: feedbackOnPrevious,
        english_variant: userPreferences?.english_variant,
        highlighted_text: highlightedText,
        highlight_id: highlightedTextId,
      };

      console.log('📤 Sending chat request:', requestData);
      
      // Increase timeout to 60 seconds and add better error handling
      const timeoutPromise = new Promise<never>((_, reject) => {
        setTimeout(() => reject(new Error('Request timeout after 60 seconds')), 60000);
      });

      const response: ChatResponse = await Promise.race([
        api.chat(requestData),
        timeoutPromise
      ]);

      console.log('📥 Received chat response:', response);
      
      setIsThinking(false);
      
      if (response && response.dialogue_response && response.dialogue_response.trim()) {
        setFullResponse(response.dialogue_response);
        setIsStreaming(true); // Start streaming the response
        setThinkingTrail(response.thinking_trail || null);
      } else {
        // Handle cases where dialogue_response might be empty or undefined
        console.warn('⚠️ Empty or invalid response received:', response);
        const fallbackMessage = `I apologize, but I received an empty response. As ${authorPersona} would say, let's try again with a different approach.`;
        setMessages(prev => [
          ...prev,
          { role: 'assistant', content: fallbackMessage }
        ]);
        setThinkingTrail('Empty response received - using fallback');
      }

    } catch (error: unknown) {
      logger.error('❌ Error sending message in useChat:', error);
      setIsThinking(false);
      setIsStreaming(false);
      
      const typedError = error as ApiError & { userMessage?: string };
      
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
        apiUrl: 'https://backend-production-41ee.up.railway.app',
        timestamp: new Date().toISOString()
      });
      
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
        fallbackResponse = `There was an issue with your request format. As ${authorPersona} would say, clarity is key in both writing and communication. Please try rephrasing your question.`;
      } else if (typedError.response?.status === 403 || typedError.response?.status === 401) {
        errorType = 'auth';
        fallbackResponse = `There was an authentication issue. As ${authorPersona} would say, proper credentials are essential. Please refresh the page and try again.`;
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
      if (setApiGlobalError && (errorType === 'network' || errorType === 'timeout' || errorType === 'auth')) {
        setApiGlobalError(`Backend connection issue (${errorType}). Backend URL: https://backend-production-41ee.up.railway.app. Please check if the server is running.`);
      }
    }
  }, [messages, editorContent, authorPersona, helpFocus, selectedLLM, userPreferences, feedbackOnPrevious, highlightedText, highlightedTextId, setApiGlobalError]);

  const handleSaveCheckpoint = useCallback(async () => {
    logger.log("Save Checkpoint clicked");
    try {
      await api.createCheckpoint({ editor_text: editorContent, chat_history: messages });
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