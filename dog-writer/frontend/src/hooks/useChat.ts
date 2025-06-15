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
      };
      
      const response: ChatResponse = await api.chat(requestData);
      
      setIsThinking(false);
      if (response.dialogue_response) {
        setFullResponse(response.dialogue_response);
        setIsStreaming(true); // Start streaming the response
      } else {
        // Handle cases where dialogue_response might be empty or undefined
        setMessages(prev => [
          ...prev,
          { role: 'assistant', content: 'I received an empty response. Please try again.' }
        ]);
      }
      setThinkingTrail(response.thinking_trail || null);

    } catch (error: unknown) {
      logger.error('Error sending message in useChat:', error);
      
      const typedError = error as ApiError & { userMessage?: string };
      
      // Use the enhanced error message from axios interceptor if available
      const userFriendlyMessage = typedError.userMessage || 'Sorry, I encountered an error. Please try again.';
      
      setMessages(prev => [
        ...prev,
        { role: 'assistant', content: userFriendlyMessage }
      ]);
      
      // Detailed error for debugging
      let specificApiError = `Error: ${typedError.message || 'Unknown error'}`;
      if (typedError.response && typedError.response.data) {
        const errorDetail = typedError.response.data.detail || typedError.response.data.error || JSON.stringify(typedError.response.data);
        specificApiError = `API error: ${typedError.response.status} - ${errorDetail}`;
      } else if (typedError.response) {
        specificApiError = `API error: ${typedError.response.status} - ${typedError.response.statusText}`;
      } else if (typedError.message?.includes('Network Error')) {
        specificApiError = 'Network error: Unable to connect to the server. Please check if the backend is running.';
      }
      
      setApiError(specificApiError);
      
      // Also set global error if the error is connection-related
      if (setApiGlobalError && (typedError.message?.includes('Network Error') || typedError.message?.includes('ECONNREFUSED'))) {
        setApiGlobalError('Backend connection failed. Please ensure the server is running.');
      }
      
      setIsThinking(false);
      setIsStreaming(false);
    }
  }, [messages, editorContent, authorPersona, helpFocus, selectedLLM, userPreferences, feedbackOnPrevious]);

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