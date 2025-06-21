import React, { createContext, useContext, ReactNode, useCallback } from 'react';
import { Document } from '../services/api';
import { useEditor } from '../hooks/useEditor';
import { useDocuments } from '../hooks/useDocuments';

export interface EditorContextType {
  // Editor state
  editorContent: string;
  setEditorContent: React.Dispatch<React.SetStateAction<string>>;
  
  // Document management
  documentManager: {
    // Core state
    documents: Document[];
    folders: any[];
    series: any[];
    templates: any[];
    currentDocument: Document | null;
    isLoading: boolean;
    error: string | null;
    
    // Advanced features
    versions: any[];
    searchResults: any[];
    writingStats: any;
    writingSessions: any[];
    writingGoals: any[];
    
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
    createFolder: (name: string, parentId?: string, color?: string) => Promise<any>;
    createSeries: (name: string, description?: string) => Promise<any>;
    moveDocument: (documentId: string, folderId?: string, seriesId?: string) => Promise<void>;
    
    // Version management
    loadVersions: (documentId: string) => Promise<void>;
    restoreVersion: (documentId: string, versionId: string) => Promise<void>;
    
    // Search
    searchDocuments: (searchRequest: any) => Promise<void>;
    clearSearch: () => void;
    
    // Templates
    createFromTemplate: (templateId: string, title: string, folderId?: string) => Promise<Document>;
    
    // Export
    exportDocument: (documentId: string, format: string, options?: any) => Promise<void>;
    
    // Analytics
    loadWritingStats: (period: 'week' | 'month' | 'year') => Promise<void>;
    createWritingGoal: (goal: any) => Promise<any>;
    
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

  // Actions
  handleSaveCheckpoint: () => void;
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
  }, [documentsHook.currentDocument, documentsHook.updateDocument, editorContent]);

  // Add the missing saveCurrentDocument method
  const saveCurrentDocument = useCallback(async () => {
    if (documentsHook.currentDocument) {
      await documentsHook.updateDocument(documentsHook.currentDocument.id, {
        content: editorContent
      });
    }
  }, [documentsHook.currentDocument, documentsHook.updateDocument, editorContent]);

  // Build context value
  const value: EditorContextType = {
    editorContent,
    setEditorContent,
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