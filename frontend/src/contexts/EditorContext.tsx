import React, { createContext, useContext, ReactNode, useCallback } from 'react';
import { Document, DocumentFolder, SearchResult } from '../services/api/types';
import { useEditor } from '../hooks/useEditor';
import { useDocuments } from '../hooks/useDocuments';

// Define proper types instead of 'any'
interface DocumentManager {
  currentDocument: Document | null;
  documents: Document[];
  folders: DocumentFolder[];
  isLoading: boolean;
  error: string | null;
  searchResults: SearchResult[];
  isSearching: boolean;
  isSaving: boolean;
  lastSaved: Date | null;
  hasUnsavedChanges: boolean;
  pendingContent: string;
  pendingTitle: string;
  
  // Methods
  createDocument: (title: string, documentType?: string, folderId?: string) => Promise<Document>;
  getDocument: (id: string) => Promise<Document>;
  updateDocument: (id: string, updates: Partial<Document>) => Promise<Document>;
  deleteDocument: (id: string) => Promise<void>;
  duplicateDocument: (id: string, newTitle?: string) => Promise<Document>;
  setCurrentDocument: (document: Document | null) => void;
  updateContent: (content: string) => void;
  updateTitle: (title: string) => void;
  saveNow: () => Promise<void>;
  refreshAll: () => Promise<void>;
  saveCurrentDocument?: () => Promise<void>;
}

interface EditorActions {
  openDocument: (document: Document) => void;
  closeDocument: () => void;
  createNewDocument: (title?: string) => Promise<void>;
  saveDocument: () => Promise<void>;
  autoSave: (content: string) => void;
}

interface EditorState {
  isDocumentOpen: boolean;
  isEditorFocused: boolean;
  hasUnsavedChanges: boolean;
  wordCount: number;
  lastSaved: Date | null;
}

interface EditorContextType {
  // Document Management
  documentManager: DocumentManager;
  
  // Editor State
  editorState?: EditorState;
  
  // Editor Actions
  editorActions?: EditorActions;
  
  // Editor Content
  editorContent: string;
  setEditorContent: (content: string) => void;
  
  // Utility functions
  setCurrentTitle?: (title: string) => void;
  setCurrentContent?: (content: string) => void;
  handleSaveCheckpoint: () => Promise<void>;
}

const EditorContext = createContext<EditorContextType | undefined>(undefined);

export const EditorProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const documentsHook = useDocuments();
  const { editorContent, setEditorContent } = useEditor({
    initialContent: documentsHook.currentDocument?.content || ''
  });

  // Handle save checkpoint
  const handleSaveCheckpoint = useCallback(async () => {
    if (documentsHook.currentDocument) {
      await documentsHook.updateDocument(documentsHook.currentDocument.id, {
        content: editorContent
      });
    }
  }, [documentsHook, editorContent]);

  // Add the missing saveCurrentDocument method
  const saveCurrentDocument = useCallback(async () => {
    if (documentsHook.currentDocument) {
      await documentsHook.updateDocument(documentsHook.currentDocument.id, {
        content: editorContent
      });
    }
  }, [documentsHook, editorContent]);

  // Build context value
  const value: EditorContextType = {
    editorContent,
    setEditorContent, // Back to original - no custom handler here
    documentManager: {
      ...documentsHook,
      saveCurrentDocument // Add the missing method
    },
    handleSaveCheckpoint,
  };

  return <EditorContext.Provider value={value}>{children}</EditorContext.Provider>;
};

export const useEditorContext = (): EditorContextType => {
  const context = useContext(EditorContext);
  if (context === undefined) {
    throw new Error('useEditorContext must be used within an EditorProvider');
  }
  return context;
};