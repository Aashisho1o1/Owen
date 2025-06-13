import React, { createContext, useContext, useState, ReactNode, useEffect, useMemo } from 'react';
import { ChatMessage } from '../services/api';
import { useApiHealth } from '../hooks/useApiHealth';
import { useChat } from '../hooks/useChat';
import { useEditor } from '../hooks/useEditor';
import { logger } from '../utils/logger';

interface WritingStyleProfile {
  formality?: string;
  sentence_complexity?: string;
  pacing?: string;
  key_vocabulary?: string[];
  literary_devices?: string[];
  regional_indicators?: string;
  [key: string]: unknown; // Allow additional properties with unknown type
}

interface UserPreferences {
  english_variant: string;
  writing_style_profile?: WritingStyleProfile;
  onboarding_completed: boolean;
  user_corrections: string[];
  writing_type?: string;
  feedback_style?: string;
  primary_goal?: string;
}

interface StyleOption {
  value: string;
  label: string;
}

interface OnboardingData {
  writing_type: string;
  feedback_style: string;
  primary_goal: string;
  english_variant: string;
}

// Define the structure of our context
interface AppContextType {
  // Author and content settings
  authorPersona: string;
  setAuthorPersona: (value: string) => void;
  helpFocus: string;
  setHelpFocus: (value: string) => void;
  selectedLLM: string;
  setSelectedLLM: (value: string) => void;
  
  // Editor state
  editorContent: string;
  setEditorContent: (content: string) => void;
  highlightedText: string | null;
  handleTextHighlighted: (text: string) => void;
  
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
  
  // Actions
  handleSaveCheckpoint: () => Promise<void>;
  
  // New personalization features
  userPreferences: UserPreferences;
  setUserPreferences: (preferences: UserPreferences) => void;
  englishVariants: StyleOption[];
  feedbackOnPrevious: string;
  setFeedbackOnPrevious: (feedback: string) => void;
  showOnboarding: boolean;
  setShowOnboarding: (show: boolean) => void;
  
  // Actions
  loadUserPreferences: () => Promise<void>;
  updateEnglishVariant: (variant: string) => void;
  submitFeedback: (originalMessage: string, aiResponse: string, feedback: string, type: string) => Promise<void>;
  analyzeWritingSample: (sample: string) => Promise<WritingStyleProfile | null>;
  completeOnboarding: (data: OnboardingData) => Promise<void>;
}

// Create the context with a default value
const AppContext = createContext<AppContextType | undefined>(undefined);

// Create a provider component
export const AppProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  // Core state
  const [authorPersona, setAuthorPersona] = useState('Ernest Hemingway');
  const [helpFocus, setHelpFocus] = useState('Dialogue Writing');
  const [selectedLLM, setSelectedLLM] = useState('Google Gemini');

  // New personalization state
  const [userPreferences, setUserPreferences] = useState<UserPreferences>({
    english_variant: 'standard',
    onboarding_completed: false,
    user_corrections: []
  });
  
  const [englishVariants, setEnglishVariants] = useState<StyleOption[]>([
    { value: 'standard', label: 'Standard English' },
    { value: 'indian', label: 'Indian English' },
    { value: 'british', label: 'British English' },
    { value: 'american', label: 'American English' }
  ]);
  
  const [feedbackOnPrevious, setFeedbackOnPrevious] = useState<string>('');
  const [showOnboarding, setShowOnboarding] = useState<boolean>(false);

  // Use our custom hooks
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

  const {
    editorContent,
    setEditorContent,
    highlightedText,
    handleTextHighlighted,
  } = useEditor({});

  const {
    messages,
    thinkingTrail,
    apiError: chatApiError,
    isStreaming,
    streamText,
    isThinking,
    handleSendMessage,
    handleSaveCheckpoint,
  } = useChat({
    authorPersona,
    helpFocus,
    editorContent,
    selectedLLM,
    setApiGlobalError,
    // Pass new personalization parameters
    userPreferences,
    feedbackOnPrevious,
  });

  // Load user preferences and style options on mount
  useEffect(() => {
    loadUserPreferences();
    loadStyleOptions();
  }, []);

  const loadUserPreferences = async () => {
    try {
      const response = await fetch('/api/chat/preferences');
      const data = await response.json();
      
      if (data.status === 'success' && data.preferences) {
        setUserPreferences(data.preferences);
        
        // Show onboarding if not completed
        if (!data.preferences.onboarding_completed) {
          setShowOnboarding(true);
        }
      }
    } catch (error) {
      logger.error('Error loading user preferences:', error);
    }
  };

  const loadStyleOptions = async () => {
    try {
      const response = await fetch('/api/chat/style-options');
      const data = await response.json();
      
      if (data.english_variants) {
        setEnglishVariants(data.english_variants);
      }
    } catch (error) {
      logger.error('Error loading style options:', error);
    }
  };

  const updateEnglishVariant = (variant: string) => {
    const updatedPreferences = { ...userPreferences, english_variant: variant };
    setUserPreferences(updatedPreferences);
  };

  const submitFeedback = async (originalMessage: string, aiResponse: string, feedback: string, type: string) => {
    try {
      const response = await fetch('/api/chat/feedback', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          original_message: originalMessage,
          ai_response: aiResponse,
          user_feedback: feedback,
          correction_type: type
        })
      });
      
      const data = await response.json();
      
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
      const response = await fetch('/api/chat/analyze-writing', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          writing_sample: sample
        })
      });
      
      const data = await response.json();
      
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
      const response = await fetch('/api/chat/onboarding', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(onboardingData)
      });
      
      const data = await response.json();
      
      if (data.success && data.user_preferences) {
        setUserPreferences(data.user_preferences);
        setShowOnboarding(false);
      }
    } catch (error) {
      logger.error('Error completing onboarding:', error);
    }
  };

  // Memoize the context value to prevent unnecessary renders
  const contextValue = useMemo(() => ({
    // Author and content settings
    authorPersona,
    setAuthorPersona,
    helpFocus,
    setHelpFocus,
    selectedLLM,
    setSelectedLLM,
    
    // Editor state
    editorContent,
    setEditorContent,
    highlightedText,
    handleTextHighlighted,
    
    // Chat state
    messages,
    handleSendMessage,
    thinkingTrail,
    isStreaming,
    streamText,
    isThinking,
    chatApiError,
    
    // API health
    apiGlobalError,
    checkApiConnection,
    
    // Actions
    handleSaveCheckpoint,
    
    // New personalization features
    userPreferences,
    setUserPreferences,
    englishVariants,
    feedbackOnPrevious,
    setFeedbackOnPrevious,
    showOnboarding,
    setShowOnboarding,
    
    // Actions
    loadUserPreferences,
    updateEnglishVariant,
    submitFeedback,
    analyzeWritingSample,
    completeOnboarding,
  }), [
    authorPersona, helpFocus, selectedLLM,
    editorContent, highlightedText,
    messages, thinkingTrail, isStreaming, streamText, isThinking, chatApiError,
    apiGlobalError,
    // Adding missing dependencies:
    setEditorContent, handleTextHighlighted,
    handleSendMessage, checkApiConnection, handleSaveCheckpoint,
    userPreferences, englishVariants, feedbackOnPrevious, showOnboarding,
    loadUserPreferences, updateEnglishVariant, submitFeedback, analyzeWritingSample, completeOnboarding
  ]);

  return (
    <AppContext.Provider value={contextValue}>
      {children}
    </AppContext.Provider>
  );
};

// Create a custom hook to use the context
export const useAppContext = (): AppContextType => {
  const context = useContext(AppContext);
  if (context === undefined) {
    throw new Error('useAppContext must be used within an AppProvider');
  }
  return context;
};

// Export the context separately
export { AppContext }; 