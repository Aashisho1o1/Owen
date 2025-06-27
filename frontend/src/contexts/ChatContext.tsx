import React, { createContext, useContext, useState, ReactNode, useEffect, useCallback } from 'react';
import { ChatMessage } from '../services/api';
import { useApiHealth } from '../hooks/useApiHealth';
import { useChat } from '../hooks/useChat';
import { useAuth } from './AuthContext';
import { logger } from '../utils/logger';
import { apiClient } from '../services/api/client';
import { 
  getUserPreferences, 
  submitUserFeedback,
  generateSuggestions,
  acceptSuggestion
} from '../services/api/chat';
import { SuggestionOption, EnhancedChatResponse, AcceptSuggestionResponse } from '../services/api/types';

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
  
  // NEW: AI Interaction Mode (Talk vs Co-Edit)
  aiMode: string;
  setAiMode: React.Dispatch<React.SetStateAction<string>>;
  
  // Text highlighting for AI feedback
  highlightedText: string;
  setHighlightedText: React.Dispatch<React.SetStateAction<string>>;
  highlightedTextId: string | null;
  setHighlightedTextId: React.Dispatch<React.SetStateAction<string | null>>;
  handleTextHighlighted: (text: string, highlightId?: string) => void;
  clearTextHighlight: () => void;
  clearAllTextHighlights: () => void;
  
  // Chat state
  messages: ChatMessage[];
  handleSendMessage: (message: string) => Promise<void>;
  thinkingTrail: string | null;
  isStreaming: boolean;
  streamText: string;
  isThinking: boolean;
  chatApiError: string | null;
  
  // NEW: Suggestions functionality
  currentSuggestions: SuggestionOption[];
  isGeneratingSuggestions: boolean;
  isAcceptingSuggestion: boolean;
  acceptedSuggestionId: string | null;
  generateTextSuggestions: (message: string) => Promise<void>;
  acceptTextSuggestion: (suggestion: SuggestionOption, onContentUpdate?: (newContent: string, replacementInfo: any) => void) => Promise<void>;
  clearSuggestions: () => void;
  
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
  const [isChatVisible, setIsChatVisible] = useState(true);
  
  // Core chat settings state
  const [authorPersona, setAuthorPersona] = useState('Ernest Hemingway');
  const [helpFocus, setHelpFocus] = useState('Dialogue Writing');
  const [selectedLLM, setSelectedLLM] = useState('Google Gemini');
  
  // NEW: AI Interaction Mode state
  const [aiMode, setAiMode] = useState('talk'); // Default to conversational mode

  // Text highlighting state
  const [highlightedText, setHighlightedText] = useState<string>('');
  const [highlightedTextId, setHighlightedTextId] = useState<string | null>(null);

  // NEW: Suggestions state
  const [currentSuggestions, setCurrentSuggestions] = useState<SuggestionOption[]>([]);
  const [isGeneratingSuggestions, setIsGeneratingSuggestions] = useState(false);
  const [isAcceptingSuggestion, setIsAcceptingSuggestion] = useState(false);
  const [acceptedSuggestionId, setAcceptedSuggestionId] = useState<string | null>(null);

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
    aiMode,  // NEW: Pass AI mode to useChat hook
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
      // Remove automatic health check - it causes race conditions
      // Health checks should only happen when explicitly requested
    } else if (!authLoading) {
      logger.info('👤 User not authenticated, using default preferences');
      // Reset to default preferences when not authenticated
      setUserPreferences({
        onboarding_completed: false,
        user_corrections: [],
        english_variant: 'US'
      });
    }
  }, [isAuthenticated, authLoading]); // Removed originalCheckApiConnection dependency

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
    // ENHANCEMENT: Always clear previous highlights before adding new ones
    if (highlightedText && highlightedText !== text) {
      // Clear the previous highlight first
      const clearEvent = new CustomEvent('applyActiveDiscussionHighlight', {
        detail: { 
          text: highlightedText, 
          highlightId: highlightedTextId || `active-discussion-${Date.now()}`,
          action: 'remove'
        }
      });
      window.dispatchEvent(clearEvent);
      
      logger.log('🧹 Cleared previous highlight before applying new one:', { 
        previousText: highlightedText.substring(0, 50) + '...',
        newText: text.substring(0, 50) + '...'
      });
    }
    
    setHighlightedText(text);
    setHighlightedTextId(highlightId || null);
    
    // Apply new highlight
    const highlightEvent = new CustomEvent('applyActiveDiscussionHighlight', {
      detail: { 
        text, 
        highlightId: highlightId || `active-discussion-${Date.now()}`,
        action: 'add'
      }
    });
    window.dispatchEvent(highlightEvent);
    
    logger.log('✨ Text highlighted for AI feedback:', { 
      text: text.substring(0, 50) + '...', 
      highlightId,
      timestamp: new Date().toISOString()
    });
  }, [highlightedText, highlightedTextId]);

  const clearTextHighlight = useCallback(() => {
    const previousText = highlightedText;
    const previousId = highlightedTextId;
    
    setHighlightedText('');
    setHighlightedTextId(null);
    
    // Dispatch event to remove active discussion highlighting
    if (previousText) {
      const clearEvent = new CustomEvent('applyActiveDiscussionHighlight', {
        detail: { 
          text: previousText, 
          highlightId: previousId || `active-discussion-${Date.now()}`,
          action: 'remove'
        }
      });
      window.dispatchEvent(clearEvent);
      
      logger.log('🧹 Text highlight cleared:', { 
        clearedText: previousText.substring(0, 50) + '...',
        timestamp: new Date().toISOString()
      });
    }
  }, [highlightedText, highlightedTextId]);

  // NEW: Force clear all highlights (for unhighlight button)
  const clearAllTextHighlights = useCallback(() => {
    // Clear state
    setHighlightedText('');
    setHighlightedTextId(null);
    
    // Dispatch event to remove ALL highlights from the editor
    const clearAllEvent = new CustomEvent('applyActiveDiscussionHighlight', {
      detail: { 
        action: 'clear-all'
      }
    });
    window.dispatchEvent(clearAllEvent);
    
    logger.log('🧹 All text highlights cleared');
  }, []);

  // NEW: Generate text suggestions (kept for manual button, but now mainly handled by useChat)
  const generateTextSuggestions = async (message: string) => {
    if (!highlightedText.trim()) {
      logger.warn('No text highlighted for suggestions');
      return;
    }

    if (aiMode !== 'co-edit') {
      logger.warn('Suggestions only available in Co-Edit mode');
      return;
    }

    setIsGeneratingSuggestions(true);
    setCurrentSuggestions([]);
    
    try {
      logger.info('🎯 Generating suggestions for highlighted text...');
      
      const requestData = {
        message,
        editor_text: editorContent,
        highlighted_text: highlightedText,
        highlight_id: highlightedTextId,
        author_persona: authorPersona,
        help_focus: helpFocus,
        chat_history: messages,
        llm_provider: selectedLLM,
        ai_mode: aiMode,
        user_preferences: userPreferences,
        feedback_on_previous: feedbackOnPrevious
      };

      const response: EnhancedChatResponse = await generateSuggestions(requestData);
      
      if (response.has_suggestions && response.suggestions.length > 0) {
        setCurrentSuggestions(response.suggestions);
        logger.info(`✨ Generated ${response.suggestions.length} suggestions`);
      } else {
        logger.warn('No suggestions generated');
      }
      
    } catch (error) {
      logger.error('Error generating suggestions:', error);
      setApiGlobalError('Failed to generate suggestions. Please try again.');
    } finally {
      setIsGeneratingSuggestions(false);
    }
  };

  // NEW: Listen for suggestions generated automatically by useChat
  useEffect(() => {
    const handleSuggestionsGenerated = (event: CustomEvent) => {
      const { suggestions, originalText, dialogueResponse } = event.detail;
      
      console.log('🎯 ChatContext received suggestionsGenerated event:', {
        suggestionsCount: suggestions?.length || 0,
        originalTextPreview: originalText?.substring(0, 50) + '...',
        hasDialogueResponse: !!dialogueResponse,
        suggestions: suggestions
      });
      
      if (suggestions && suggestions.length > 0) {
        console.log('✨ Setting suggestions in ChatContext:', suggestions);
        setCurrentSuggestions(suggestions);
        setIsGeneratingSuggestions(false);
        
        // Force a re-render by updating a timestamp
        console.log('📝 Current suggestions state updated with', suggestions.length, 'suggestions');
      } else {
        console.warn('⚠️ No valid suggestions received in event');
        setCurrentSuggestions([]);
      }
    };

    console.log('🔧 ChatContext: Setting up suggestionsGenerated event listener');
    window.addEventListener('suggestionsGenerated', handleSuggestionsGenerated as EventListener);
    
    return () => {
      console.log('🧹 ChatContext: Cleaning up suggestionsGenerated event listener');
      window.removeEventListener('suggestionsGenerated', handleSuggestionsGenerated as EventListener);
    };
  }, []);

  // NEW: Accept a text suggestion
  const acceptTextSuggestion = async (
    suggestion: SuggestionOption, 
    onContentUpdate?: (newContent: string, replacementInfo: any) => void
  ) => {
    setIsAcceptingSuggestion(true);
    setAcceptedSuggestionId(suggestion.id);
    
    try {
      logger.info(`✅ Accepting suggestion: ${suggestion.id}`);
      
      const requestData = {
        suggestion_id: suggestion.id,
        original_text: highlightedText,
        suggested_text: suggestion.text,
        editor_content: editorContent,
        position_info: { highlight_id: highlightedTextId }
      };

      const response: AcceptSuggestionResponse = await acceptSuggestion(requestData);
      
      if (response.success) {
        logger.info('✅ Suggestion accepted successfully');
        
        // Update the editor content through the callback if provided
        if (onContentUpdate) {
          onContentUpdate(response.updated_content, response.replacement_info);
        } else {
          // Fallback: Dispatch event to update editor content
          window.dispatchEvent(new CustomEvent('updateEditorContent', {
            detail: {
              newContent: response.updated_content,
              replacementInfo: response.replacement_info,
              highlightNewText: true
            }
          }));
        }
        
        // Clear suggestions and highlighting
        setCurrentSuggestions([]);
        setHighlightedText('');
        setHighlightedTextId(null);
        
        // Clear highlight from editor
        const clearEvent = new CustomEvent('applyActiveDiscussionHighlight', {
          detail: { action: 'clear-all' }
        });
        window.dispatchEvent(clearEvent);
        
      } else {
        logger.error('Failed to accept suggestion:', response.error);
        setApiGlobalError(response.error || 'Failed to accept suggestion');
      }
      
    } catch (error) {
      logger.error('Error accepting suggestion:', error);
      setApiGlobalError('Failed to accept suggestion. Please try again.');
    } finally {
      setIsAcceptingSuggestion(false);
      setAcceptedSuggestionId(null);
    }
  };

  // NEW: Clear suggestions
  const clearSuggestions = () => {
    setCurrentSuggestions([]);
    setAcceptedSuggestionId(null);
  };

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
    aiMode,
    setAiMode,
    highlightedText,
    setHighlightedText,
    highlightedTextId,
    setHighlightedTextId,
    handleTextHighlighted,
    clearTextHighlight,
    clearAllTextHighlights,
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
    currentSuggestions,
    isGeneratingSuggestions,
    isAcceptingSuggestion,
    acceptedSuggestionId,
    generateTextSuggestions,
    acceptTextSuggestion,
    clearSuggestions,
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