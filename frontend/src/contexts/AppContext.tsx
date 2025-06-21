import React, { createContext, useContext, ReactNode } from 'react';
import { ChatProvider } from './ChatContext';
import { EditorProvider, useEditorContext } from './EditorContext';
import { UIProvider } from './UIContext';

// Simple coordinating context that just provides access to other contexts
export interface AppContextType {
  // This coordinator ensures all specialized contexts are properly initialized
  initialized: boolean;
}

const AppContext = createContext<AppContextType | undefined>(undefined);

// Coordinating provider that combines all specialized providers
export const AppProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  return (
    <UIProvider>
      <EditorProvider>
        <AppProviderInner>
          {children}
        </AppProviderInner>
      </EditorProvider>
    </UIProvider>
  );
};

// Inner provider that has access to editor content for ChatProvider
const AppProviderInner: React.FC<{ children: ReactNode }> = ({ children }) => {
  const { editorContent } = useEditorContext();

  return (
    <ChatProvider editorContent={editorContent}>
      <AppContext.Provider value={{ initialized: true }}>
        {children}
      </AppContext.Provider>
    </ChatProvider>
  );
};

// Legacy hook for backward compatibility
export const useAppContext = (): AppContextType => {
  const context = useContext(AppContext);
  if (context === undefined) {
    throw new Error('useAppContext must be used within an AppProvider');
  }
  return context;
};

// Export the context separately (legacy)
export { AppContext }; 