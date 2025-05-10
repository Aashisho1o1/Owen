import React, { createContext, useContext, useState, ReactNode, useMemo } from 'react';
import { ChatMessage } from '../services/api';
import { useApiHealth } from '../hooks/useApiHealth';
import { useChat } from '../hooks/useChat';
import { useEditor } from '../hooks/useEditor';

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
}

// Create the context with a default value
const AppContext = createContext<AppContextType | undefined>(undefined);

// Create a provider component
export const AppProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  // Core state
  const [authorPersona, setAuthorPersona] = useState('Ernest Hemingway');
  const [helpFocus, setHelpFocus] = useState('Dialogue Writing');
  const [selectedLLM, setSelectedLLM] = useState('Google Gemini');

  // Use our custom hooks
  const { 
    apiGlobalError, 
    setApiGlobalError, 
    checkApiConnection 
  } = useApiHealth();

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
  });

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
  }), [
    authorPersona, helpFocus, selectedLLM,
    editorContent, highlightedText,
    messages, thinkingTrail, isStreaming, streamText, isThinking, chatApiError,
    apiGlobalError,
    // Adding missing dependencies:
    setEditorContent, handleTextHighlighted,
    handleSendMessage, checkApiConnection, handleSaveCheckpoint
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