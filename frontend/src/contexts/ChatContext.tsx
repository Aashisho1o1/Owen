import React, { createContext, useContext, useState, ReactNode, useEffect, useCallback } from 'react';
import { ChatMessage } from '../services/api';
import { useApiHealth } from '../hooks/useApiHealth';
import { useChat } from '../hooks/useChat';
import { useAuth } from './AuthContext';
import { logger } from '../utils/logger';
import { apiClient } from '../services/api/client';
import { getUserPreferences, submitUserFeedback } from '../services/api/chat';

interface WritingStyleProfile {
  formality?: string;
  sentence_complexity?: string;
  pacing?: string;
  key_vocabulary?: string[];
  literary_devices?: string[];
  regional_indicators?: string;
  [key: string]: unknown;
}

interface UserPreferences {
  writing_style_profile?: WritingStyleProfile;
  onboarding_completed: boolean;
  user_corrections: string[];
  writing_type?: string;
  feedback_style?: string;
  primary_goal?: string;
  english_variant?: string; // Add missing property to fix linter error
}

interface OnboardingData {
  writing_type: string;
  feedback_style: string;
  primary_goal: string;
}

export interface ChatContextType {
  // Chat visibility and control
  isChatVisible: boolean;
  toggleChat: () => void;
  openChatWithText: (text: string) => void;
  
  // Author and content settings
  authorPersona: string;
  setAuthorPersona: React.Dispatch<React.SetStateAction<string>>;
  helpFocus: string;
  setHelpFocus: React.Dispatch<React.SetStateAction<string>>;
  selectedLLM: string;
  setSelectedLLM: React.Dispatch<React.SetStateAction<string>>;
  
  // Text highlighting for AI feedback
  highlightedText: string;
  setHighlightedText: React.Dispatch<React.SetStateAction<string>>;
  highlightedTextId: string | null;
  setHighlightedTextId: React.Dispatch<React.SetStateAction<string | null>>;
  handleTextHighlighted: (text: string, highlightId?: string) => void;
  clearTextHighlight: () => void;
  
  // Chat state
  messages: ChatMessage[];
  handleSendMessage: (message: string) => Promise<void>;
  thinkingTrail: string | null;
  isStreaming: boolean;
  streamText: string;
  isThinking: boolean;
  chatApiError: string | null;
  
  // API health
  apiGlobalError: string | null;
  checkApiConnection: () => Promise<boolean>;
  
  // Personalization features
  userPreferences: UserPreferences;
  setUserPreferences: (preferences: UserPreferences) => void;
  feedbackOnPrevious: string;
  setFeedbackOnPrevious: (feedback: string) => void;
  showOnboarding: boolean;
  setShowOnboarding: (show: boolean) => void;
  
  // Actions
  loadUserPreferences: () => Promise<void>;
  submitFeedback: (originalMessage: string, aiResponse: string, feedback: string, type: string) => Promise<void>;
  analyzeWritingSample: (sample: string) => Promise<WritingStyleProfile | null>;
  completeOnboarding: (data: OnboardingData) => Promise<void>;
}

const ChatContext = createContext<ChatContextType | undefined>(undefined);

export const ChatProvider: React.FC<{ children: ReactNode; editorContent: string }> = ({ 
  children, 
  editorContent 
}) => {
  // Get authentication state
  const { isAuthenticated, isLoading: authLoading } = useAuth();
  
  // Chat visibility state
  const [isChatVisible, setIsChatVisible] = useState(false);
  
  // Core chat settings state
  const [authorPersona, setAuthorPersona] = useState('Ernest Hemingway');
  const [helpFocus, setHelpFocus] = useState('Dialogue Writing');
  const [selectedLLM, setSelectedLLM] = useState('Google Gemini');

  // Text highlighting state
  const [highlightedText, setHighlightedText] = useState<string>('');
  const [highlightedTextId, setHighlightedTextId] = useState<string | null>(null);

  // Chat control methods
  const toggleChat = useCallback(() => {
    setIsChatVisible(prev => !prev);
  }, []);

  const openChatWithText = useCallback((text: string) => {
    setHighlightedText(text);
    setIsChatVisible(true);
  }, []);

  // Personalization state
  const [userPreferences, setUserPreferences] = useState<UserPreferences>({
    onboarding_completed: false,
    user_corrections: [],
    english_variant: 'US' // Add default value
  });
  
  const [feedbackOnPrevious, setFeedbackOnPrevious] = useState<string>('');
  const [showOnboarding, setShowOnboarding] = useState<boolean>(false);

  // API health hook
  const { 
    apiGlobalError, 
    setApiGlobalError, 
    checkApiConnection: originalCheckApiConnection
  } = useApiHealth();

  // Fix the return type issue by wrapping the function
  const checkApiConnection = async (): Promise<boolean> => {
    try {
      await originalCheckApiConnection();
      return true;
    } catch (error) {
      logger.error('API connection check failed:', error);
      return false;
    }
  };

  // Chat hook with all necessary parameters
  const {
    messages,
    thinkingTrail,
    apiError: chatApiError,
    isStreaming,
    streamText,
    isThinking,
    handleSendMessage,
  } = useChat({
    authorPersona,
    helpFocus,
    editorContent,
    selectedLLM,
    setApiGlobalError,
    userPreferences,
    feedbackOnPrevious,
    highlightedText,
    highlightedTextId: highlightedTextId || undefined, // Convert null to undefined
  });

  // Load user preferences ONLY when authenticated
  useEffect(() => {
    // Only load preferences if user is authenticated and auth is not loading
    if (isAuthenticated && !authLoading) {
      logger.info('🔐 User authenticated, loading preferences...');
      loadUserPreferences();
      // Also run a health check now that authentication is ready
      originalCheckApiConnection().catch(error => {
        logger.warn('Health check failed after authentication:', error);
      });
    } else if (!authLoading) {
      logger.info('👤 User not authenticated, using default preferences');
      // Reset to default preferences when not authenticated
      setUserPreferences({
        onboarding_completed: false,
        user_corrections: [],
        english_variant: 'US'
      });
    }
  }, [isAuthenticated, authLoading, originalCheckApiConnection]); // Depend on authentication state

  const loadUserPreferences = async () => {
    try {
      // Double-check authentication before making the API call
      if (!isAuthenticated) {
        logger.warn('❌ Attempted to load preferences without authentication');
        return;
      }
      
      const data = await getUserPreferences();
      
      if (data.status === 'success' && data.preferences) {
        setUserPreferences(data.preferences);
        
        // Show onboarding if not completed
        if (!data.preferences.onboarding_completed) {
          setShowOnboarding(true);
        }
      }
    } catch (error) {
      logger.error('Error loading user preferences:', error);
      // Don't show global error for preferences - this is expected when not authenticated
    }
  };

  const submitFeedback = async (originalMessage: string, aiResponse: string, feedback: string, type: string) => {
    try {
      const data = await submitUserFeedback({
        original_message: originalMessage,
        ai_response: aiResponse,
        user_feedback: feedback,
        correction_type: type
      });
      
      if (data.status === 'success') {
        // Reload preferences to get updated corrections
        await loadUserPreferences();
      }
    } catch (error) {
      logger.error('Error submitting feedback:', error);
    }
  };

  const analyzeWritingSample = async (sample: string): Promise<WritingStyleProfile | null> => {
    try {
      const response = await apiClient.post('/api/chat/analyze-writing', {
        writing_sample: sample
      });
      
      const data = response.data;
      
      if (data.success && data.style_profile) {
        // Update user preferences with analyzed style
        const updatedPreferences = { 
          ...userPreferences, 
          writing_style_profile: data.style_profile 
        };
        setUserPreferences(updatedPreferences);
        return data.style_profile;
      }
      
      return null;
    } catch (error) {
      logger.error('Error analyzing writing sample:', error);
      return null;
    }
  };

  const completeOnboarding = async (onboardingData: OnboardingData) => {
    try {
      const response = await apiClient.post('/api/chat/onboarding', onboardingData);
      
      const data = response.data;
      
      if (data.success && data.user_preferences) {
        setUserPreferences(data.user_preferences);
        setShowOnboarding(false);
      }
    } catch (error) {
      logger.error('Error completing onboarding:', error);
    }
  };

  // Text highlighting handlers
  const handleTextHighlighted = useCallback((text: string, highlightId?: string) => {
    setHighlightedText(text);
    setHighlightedTextId(highlightId || null);
    logger.log('Text highlighted for AI feedback:', { text: text.substring(0, 50) + '...', highlightId });
  }, []);

  const clearTextHighlight = useCallback(() => {
    setHighlightedText('');
    setHighlightedTextId(null);
    logger.log('Text highlight cleared');
  }, []);

  // Build context value
  const value: ChatContextType = {
    isChatVisible,
    toggleChat,
    openChatWithText,
    authorPersona,
    setAuthorPersona,
    helpFocus,
    setHelpFocus,
    selectedLLM,
    setSelectedLLM,
    highlightedText,
    setHighlightedText,
    highlightedTextId,
    setHighlightedTextId,
    handleTextHighlighted,
    clearTextHighlight,
    messages,
    handleSendMessage,
    thinkingTrail,
    isStreaming,
    streamText,
    isThinking,
    chatApiError,
    apiGlobalError,
    checkApiConnection,
    userPreferences,
    setUserPreferences,
    feedbackOnPrevious,
    setFeedbackOnPrevious,
    showOnboarding,
    setShowOnboarding,
    loadUserPreferences,
    submitFeedback,
    analyzeWritingSample,
    completeOnboarding,
  };

  return <ChatContext.Provider value={value}>{children}</ChatContext.Provider>;
};

export const useChatContext = (): ChatContextType => {
  const context = useContext(ChatContext);
  if (context === undefined) {
    throw new Error('useChatContext must be used within a ChatProvider');
  }
  return context;
}; 