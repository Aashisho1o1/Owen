import React, { createContext, useContext, useState, ReactNode, useEffect, useMemo, useCallback } from 'react';
import { 
  ChatMessage, 
  Document, 
  DocumentFolder, 
  DocumentSeries, 
  DocumentTemplate, 
  DocumentVersion, 
  SearchResult, 
  SearchRequest,
  WritingGoal,
  WritingSession
} from '../services/api';
import { useApiHealth } from '../hooks/useApiHealth';
import { useChat } from '../hooks/useChat';
import { useEditor } from '../hooks/useEditor';
import { useDocuments } from '../hooks/useDocuments';
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
}

export interface AppContextType {
  // Author and content settings
  authorPersona: string;
  setAuthorPersona: React.Dispatch<React.SetStateAction<string>>;
  helpFocus: string;
  setHelpFocus: React.Dispatch<React.SetStateAction<string>>;
  selectedLLM: string;
  setSelectedLLM: React.Dispatch<React.SetStateAction<string>>;
  
  // Editor state
  editorContent: string;
  setEditorContent: React.Dispatch<React.SetStateAction<string>>;
  
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
  
  // Actions
  handleSaveCheckpoint: () => void;
  
  // New personalization features
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

  // Document management
  documentManager: {
    // Core state
    documents: Document[];
    folders: DocumentFolder[];
    series: DocumentSeries[];
    templates: DocumentTemplate[];
    currentDocument: Document | null;
    isLoading: boolean;
    error: string | null;
    
    // Advanced features
    versions: DocumentVersion[];
    searchResults: SearchResult[];
    writingStats: any;
    writingSessions: WritingSession[];
    writingGoals: WritingGoal[];
    
    // Auto-save status
    isSaving: boolean;
    lastSaved: Date | null;
    hasUnsavedChanges: boolean;
    
    // Document operations
    createDocument: (title: string, documentType?: string, folderId?: string, seriesId?: string) => Promise<Document>;
    getDocument: (id: string) => Promise<Document>;
    updateDocument: (id: string, updates: Partial<Document>) => Promise<Document>;
    deleteDocument: (id: string) => Promise<void>;
    duplicateDocument: (id: string, newTitle?: string) => Promise<Document>;
    
    // Organization
    createFolder: (name: string, parentId?: string, color?: string) => Promise<DocumentFolder>;
    createSeries: (name: string, description?: string) => Promise<DocumentSeries>;
    moveDocument: (documentId: string, folderId?: string, seriesId?: string) => Promise<void>;
    
    // Version management
    loadVersions: (documentId: string) => Promise<void>;
    restoreVersion: (documentId: string, versionId: string) => Promise<void>;
    
    // Search
    searchDocuments: (searchRequest: SearchRequest) => Promise<void>;
    clearSearch: () => void;
    
    // Templates
    createFromTemplate: (templateId: string, title: string, folderId?: string) => Promise<Document>;
    
    // Export
    exportDocument: (documentId: string, format: string, options?: any) => Promise<void>;
    
    // Analytics
    loadWritingStats: (period: 'week' | 'month' | 'year') => Promise<void>;
    createWritingGoal: (goal: Omit<WritingGoal, 'id' | 'user_id' | 'current_words'>) => Promise<WritingGoal>;
    
    // Collaboration
    shareDocument: (documentId: string, email: string, permission: 'view' | 'comment' | 'edit') => Promise<void>;
    
    // Document synchronization
    setCurrentDocument: (document: Document | null) => void;
    saveCurrentDocument: () => Promise<void>;
    
    // Utility functions
    getWordCount: (text: string) => number;
    getDocumentsByFolder: (folderId: string) => Document[];
    getDocumentsBySeries: (seriesId: string) => Document[];
    getRecentDocuments: (limit?: number) => Document[];
    getTotalWordCount: () => number;
    refreshAll: () => Promise<void>;
  };

  // Auth Modal State
  showAuthModal: boolean;
  setShowAuthModal: React.Dispatch<React.SetStateAction<boolean>>;
  authMode: 'signin' | 'signup';
  setAuthMode: React.Dispatch<React.SetStateAction<'signin' | 'signup'>>;
}

// Create the context with a default value
const AppContext = createContext<AppContextType | undefined>(undefined);

// Create a provider component
export const AppProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  // Core state
  const [authorPersona, setAuthorPersona] = useState('Ernest Hemingway');
  const [helpFocus, setHelpFocus] = useState('Dialogue Writing');
  const [selectedLLM, setSelectedLLM] = useState('Google Gemini');

  // Text highlighting state
  const [highlightedText, setHighlightedText] = useState<string>('');
  const [highlightedTextId, setHighlightedTextId] = useState<string | null>(null);

  // New personalization state
  const [userPreferences, setUserPreferences] = useState<UserPreferences>({
    onboarding_completed: false,
    user_corrections: []
  });
  
  const [feedbackOnPrevious, setFeedbackOnPrevious] = useState<string>('');
  const [showOnboarding, setShowOnboarding] = useState<boolean>(false);

  // Auth Modal State
  const [showAuthModal, setShowAuthModal] = useState(false);
  const [authMode, setAuthMode] = useState<'signin' | 'signup'>('signin');

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
    handleTextHighlighted,
  } = useEditor({});

  // Text highlighting handlers
  const handleTextHighlightedWithId = useCallback((text: string, highlightId?: string) => {
    setHighlightedText(text);
    setHighlightedTextId(highlightId || null);
    
    // Also call the editor's handler if it exists
    if (handleTextHighlighted) {
      handleTextHighlighted(text);
    }
    
    logger.log('Text highlighted for AI feedback:', { text: text.substring(0, 50) + '...', highlightId });
  }, [handleTextHighlighted]);

  const clearTextHighlight = useCallback(() => {
    setHighlightedText('');
    setHighlightedTextId(null);
    logger.log('Text highlight cleared');
  }, []);

  // Document management hook
  const documentsHook = useDocuments();

  // Sync editor content with current document
  useEffect(() => {
    if (documentsHook.currentDocument && !documentsHook.hasUnsavedChanges) {
      setEditorContent(documentsHook.currentDocument.content);
    }
  }, [documentsHook.currentDocument, documentsHook.hasUnsavedChanges, setEditorContent]);

  // Sync editor changes with document auto-save
  useEffect(() => {
    if (documentsHook.currentDocument) {
      documentsHook.updateContent(editorContent);
    }
  }, [editorContent, documentsHook.currentDocument, documentsHook.updateContent]);

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
    // Pass highlighted text parameters
    highlightedText,
    highlightedTextId,
  });

  // Load user preferences on mount
  useEffect(() => {
    loadUserPreferences();
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
  const value = useMemo(() => ({
    authorPersona,
    setAuthorPersona,
    helpFocus,
    setHelpFocus,
    selectedLLM,
    setSelectedLLM,
    editorContent,
    setEditorContent,
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
    handleSaveCheckpoint,
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
    documentManager: {
      documents: documentsHook.documents,
      folders: documentsHook.folders,
      series: documentsHook.series,
      templates: documentsHook.templates,
      currentDocument: documentsHook.currentDocument,
      isLoading: documentsHook.isLoading,
      error: documentsHook.error,
      
      versions: documentsHook.versions,
      searchResults: documentsHook.searchResults,
      writingStats: documentsHook.writingStats,
      writingSessions: documentsHook.writingSessions,
      writingGoals: documentsHook.writingGoals,
      
      isSaving: documentsHook.isSaving,
      lastSaved: documentsHook.lastSaved,
      hasUnsavedChanges: documentsHook.hasUnsavedChanges,
      
      createDocument: documentsHook.createDocument,
      getDocument: documentsHook.getDocument,
      updateDocument: documentsHook.updateDocument,
      deleteDocument: documentsHook.deleteDocument,
      duplicateDocument: documentsHook.duplicateDocument,
      
      createFolder: documentsHook.createFolder,
      createSeries: documentsHook.createSeries,
      moveDocument: documentsHook.moveDocument,
      
      loadVersions: documentsHook.loadVersions,
      restoreVersion: documentsHook.restoreVersion,
      
      searchDocuments: documentsHook.searchDocuments,
      clearSearch: documentsHook.clearSearch,
      
      createFromTemplate: documentsHook.createFromTemplate,
      
      exportDocument: documentsHook.exportDocument,
      
      loadWritingStats: documentsHook.loadWritingStats,
      createWritingGoal: documentsHook.createWritingGoal,
      
      shareDocument: documentsHook.shareDocument,
      
      setCurrentDocument: (document: Document | null) => {
        documentsHook.setCurrentDocument(document);
        if (document) {
          setEditorContent(document.content);
        } else {
          setEditorContent('');
        }
      },
      
      saveCurrentDocument: async () => {
        await documentsHook.saveNow();
      },
      
      getWordCount: documentsHook.getWordCount,
      getDocumentsByFolder: documentsHook.getDocumentsByFolder,
      getDocumentsBySeries: documentsHook.getDocumentsBySeries,
      getRecentDocuments: documentsHook.getRecentDocuments,
      getTotalWordCount: documentsHook.getTotalWordCount,
      refreshAll: documentsHook.refreshAll,
    },
    showAuthModal,
    setShowAuthModal,
    authMode,
    setAuthMode,
  }), [
    authorPersona,
    helpFocus,
    selectedLLM,
    editorContent,
    highlightedText,
    highlightedTextId,
    messages,
    thinkingTrail,
    isStreaming,
    streamText,
    isThinking,
    chatApiError,
    apiGlobalError,
    userPreferences,
    feedbackOnPrevious,
    showOnboarding,
    documentManager,
    showAuthModal,
    authMode
  ]);

  return <AppContext.Provider value={value}>{children}</AppContext.Provider>;
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