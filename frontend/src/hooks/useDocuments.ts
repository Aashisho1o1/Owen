import { useState, useEffect, useCallback, useRef } from 'react';
import { useAuth } from '../contexts/AuthContext';
import * as api from '../services/api';
import { 
  Document, 
  DocumentFolder, 
  DocumentTemplate,
  SearchRequest,
  SearchResult
} from '../services/api';

// MVP-focused DocumentState - removed analytics, versions, series, goals
interface DocumentState {
  documents: Document[];
  folders: DocumentFolder[];
  templates: DocumentTemplate[];
  currentDocument: Document | null;
  isLoading: boolean;
  error: string | null;
  
  // Search
  searchResults: SearchResult[];
  isSearching: boolean;
  
  // Auto-save
  isSaving: boolean;
  lastSaved: Date | null;
  hasUnsavedChanges: boolean;
  pendingContent: string;
  pendingTitle: string;
}

// MVP-focused UseDocumentsReturn interface
interface UseDocumentsReturn extends DocumentState {
  // Document CRUD
  createDocument: (title: string, documentType?: string, folderId?: string) => Promise<Document>;
  getDocument: (id: string) => Promise<Document>;
  updateDocument: (id: string, updates: Partial<Document>) => Promise<Document>;
  deleteDocument: (id: string) => Promise<void>;
  duplicateDocument: (id: string, newTitle?: string) => Promise<Document>;
  
  // Folder management
  createFolder: (name: string, parentId?: string, color?: string) => Promise<DocumentFolder>;
  updateFolder: (id: string, updates: Partial<DocumentFolder>) => Promise<DocumentFolder>;
  deleteFolder: (id: string, moveDocumentsTo?: string) => Promise<void>;
  moveDocument: (documentId: string, folderId?: string) => Promise<void>;
  
  // Search
  searchDocuments: (searchRequest: SearchRequest) => Promise<void>;
  clearSearch: () => void;
  
  // Templates
  createFromTemplate: (templateId: string, title: string, folderId?: string) => Promise<Document>;
  
  // Auto-save & sync
  setCurrentDocument: (document: Document | null) => void;
  updateContent: (content: string) => void;
  updateTitle: (title: string) => void;
  saveNow: () => Promise<void>;
  
  // Utility functions
  getWordCount: (text: string) => number;
  getDocumentsByFolder: (folderId: string) => Document[];
  getRecentDocuments: (limit?: number) => Document[];
  getTotalWordCount: () => number;
  
  // Refresh data
  refreshAll: () => Promise<void>;
}

export const useDocuments = (): UseDocumentsReturn => {
  const { user } = useAuth();
  const [state, setState] = useState<DocumentState>({
    documents: [],
    folders: [],
    templates: [],
    currentDocument: null,
    isLoading: false,
    error: null,
    searchResults: [],
    isSearching: false,
    isSaving: false,
    lastSaved: null,
    hasUnsavedChanges: false,
    pendingContent: '',
    pendingTitle: '',
  });

  const autoSaveTimerRef = useRef<NodeJS.Timeout | null>(null);
  const lastContentRef = useRef<string>('');
  const lastTitleRef = useRef<string>('');

  // Auto-save function
  const performAutoSave = useCallback(async () => {
    if (!state.currentDocument || !state.hasUnsavedChanges) return;

    const contentChanged = state.pendingContent !== lastContentRef.current;
    const titleChanged = state.pendingTitle !== lastTitleRef.current;

    if (!contentChanged && !titleChanged) return;

    try {
      setState(prev => ({ ...prev, isSaving: true }));
      
      const updates: Partial<Document> = {};
      if (contentChanged) updates.content = state.pendingContent;
      if (titleChanged) updates.title = state.pendingTitle;

      await api.updateDocument(state.currentDocument.id, updates);
      
      lastContentRef.current = state.pendingContent;
      lastTitleRef.current = state.pendingTitle;
      
      setState(prev => ({
        ...prev,
        isSaving: false,
        lastSaved: new Date(),
        hasUnsavedChanges: false,
        currentDocument: prev.currentDocument ? {
          ...prev.currentDocument,
          ...updates,
          updated_at: new Date().toISOString()
        } : null
      }));
    } catch (error) {
      setState(prev => ({ 
        ...prev, 
        isSaving: false, 
        error: error instanceof Error ? error.message : 'Failed to save document' 
      }));
    }
  }, [state.currentDocument, state.hasUnsavedChanges, state.pendingContent, state.pendingTitle]);

  // Setup auto-save timer
  useEffect(() => {
    if (state.hasUnsavedChanges && state.currentDocument) {
      autoSaveTimerRef.current = setTimeout(performAutoSave, 2000);
    }
    
    return () => {
      if (autoSaveTimerRef.current) {
        clearTimeout(autoSaveTimerRef.current);
      }
    };
  }, [performAutoSave, state.hasUnsavedChanges, state.currentDocument]);

  // Load initial data - MVP VERSION (only endpoints that exist)
  const refreshAll = useCallback(async () => {
    if (!user) return;
    
    setState(prev => ({ ...prev, isLoading: true, error: null }));
    
    try {
      // Only call endpoints that exist in MVP backend
      const [documents, folders, templates] = await Promise.all([
        api.getDocuments(),
        api.getFolders(),
        api.getTemplates()
      ]);
      
      setState(prev => ({
        ...prev,
        documents: documents.documents || [],
        folders,
        templates,
        isLoading: false
      }));
    } catch (error) {
      setState(prev => ({
        ...prev,
        error: error instanceof Error ? error.message : 'Failed to load data',
        isLoading: false
      }));
    }
  }, [user]);

  useEffect(() => {
    refreshAll();
  }, [refreshAll]);

  // Document CRUD operations - simplified without series
  const createDocument = useCallback(async (
    title: string, 
    documentType: string = 'novel', 
    folderId?: string
  ): Promise<Document> => {
    try {
      setState(prev => ({ ...prev, isLoading: true }));
      
      const document = await api.createDocument({
        title,
        content: '',
        document_type: documentType,
        folder_id: folderId
      });
      
      setState(prev => ({
        ...prev,
        documents: [document, ...prev.documents],
        isLoading: false
      }));
      
      return document;
    } catch (error) {
      setState(prev => ({
        ...prev,
        error: error instanceof Error ? error.message : 'Failed to create document',
        isLoading: false
      }));
      throw error;
    }
  }, []);

  const getDocument = useCallback(async (id: string): Promise<Document> => {
    try {
      const document = await api.getDocument(id);
      return document;
    } catch (error) {
      setState(prev => ({
        ...prev,
        error: error instanceof Error ? error.message : 'Failed to get document'
      }));
      throw error;
    }
  }, []);

  const updateDocument = useCallback(async (id: string, updates: Partial<Document>): Promise<Document> => {
    try {
      const updatedDocument = await api.updateDocument(id, updates);
      
      setState(prev => ({
        ...prev,
        documents: prev.documents.map(doc => 
          doc.id === id ? updatedDocument : doc
        ),
        currentDocument: prev.currentDocument?.id === id ? updatedDocument : prev.currentDocument
      }));
      
      return updatedDocument;
    } catch (error) {
      setState(prev => ({
        ...prev,
        error: error instanceof Error ? error.message : 'Failed to update document'
      }));
      throw error;
    }
  }, []);

  const deleteDocument = useCallback(async (id: string): Promise<void> => {
    try {
      await api.deleteDocument(id);
      
      setState(prev => ({
        ...prev,
        documents: prev.documents.filter(doc => doc.id !== id),
        currentDocument: prev.currentDocument?.id === id ? null : prev.currentDocument
      }));
    } catch (error) {
      setState(prev => ({
        ...prev,
        error: error instanceof Error ? error.message : 'Failed to delete document'
      }));
      throw error;
    }
  }, []);

  const duplicateDocument = useCallback(async (id: string, newTitle?: string): Promise<Document> => {
    try {
      const originalDoc = state.documents.find(doc => doc.id === id);
      if (!originalDoc) throw new Error('Document not found');
      
      const duplicatedDoc = await api.createDocument({
        title: newTitle || `${originalDoc.title} (Copy)`,
        content: originalDoc.content,
        document_type: originalDoc.document_type,
        folder_id: originalDoc.folder_id
      });
      
      setState(prev => ({
        ...prev,
        documents: [duplicatedDoc, ...prev.documents]
      }));
      
      return duplicatedDoc;
    } catch (error) {
      setState(prev => ({
        ...prev,
        error: error instanceof Error ? error.message : 'Failed to duplicate document'
      }));
      throw error;
    }
  }, [state.documents]);

  // Folder management
  const createFolder = useCallback(async (name: string, parentId?: string, color?: string): Promise<DocumentFolder> => {
    try {
      const folder = await api.createFolder({ name, parent_id: parentId, color });
      
      setState(prev => ({
        ...prev,
        folders: [...prev.folders, folder]
      }));
      
      return folder;
    } catch (error) {
      setState(prev => ({
        ...prev,
        error: error instanceof Error ? error.message : 'Failed to create folder'
      }));
      throw error;
    }
  }, []);

  const updateFolder = useCallback(async (id: string, updates: Partial<DocumentFolder>): Promise<DocumentFolder> => {
    try {
      const updatedFolder = await api.updateFolder(id, updates);
      
      setState(prev => ({
        ...prev,
        folders: prev.folders.map(folder => 
          folder.id === id ? updatedFolder : folder
        )
      }));
      
      return updatedFolder;
    } catch (error) {
      setState(prev => ({
        ...prev,
        error: error instanceof Error ? error.message : 'Failed to update folder'
      }));
      throw error;
    }
  }, []);

  const deleteFolder = useCallback(async (id: string, moveDocumentsTo?: string): Promise<void> => {
    try {
      await api.deleteFolder(id);
      
      setState(prev => ({
        ...prev,
        folders: prev.folders.filter(folder => folder.id !== id),
        documents: prev.documents.map(doc => 
          doc.folder_id === id 
            ? { ...doc, folder_id: moveDocumentsTo || undefined }
            : doc
        )
      }));
    } catch (error) {
      setState(prev => ({
        ...prev,
        error: error instanceof Error ? error.message : 'Failed to delete folder'
      }));
      throw error;
    }
  }, []);

  const moveDocument = useCallback(async (documentId: string, folderId?: string): Promise<void> => {
    try {
      await api.updateDocument(documentId, { folder_id: folderId });
      
      setState(prev => ({
        ...prev,
        documents: prev.documents.map(doc => 
          doc.id === documentId ? { ...doc, folder_id: folderId } : doc
        )
      }));
    } catch (error) {
      setState(prev => ({
        ...prev,
        error: error instanceof Error ? error.message : 'Failed to move document'
      }));
      throw error;
    }
  }, []);

  // Search functionality
  const searchDocuments = useCallback(async (searchRequest: SearchRequest): Promise<void> => {
    try {
      setState(prev => ({ ...prev, isSearching: true }));
      
      const results = await api.searchDocuments(searchRequest);
      
      setState(prev => ({
        ...prev,
        searchResults: results,
        isSearching: false
      }));
    } catch (error) {
      setState(prev => ({
        ...prev,
        error: error instanceof Error ? error.message : 'Search failed',
        isSearching: false
      }));
    }
  }, []);

  const clearSearch = useCallback(() => {
    setState(prev => ({
      ...prev,
      searchResults: [],
      isSearching: false
    }));
  }, []);

  // Template functionality
  const createFromTemplate = useCallback(async (templateId: string, title: string, folderId?: string): Promise<Document> => {
    try {
      const document = await api.createDocumentFromTemplate({
        template_id: templateId,
        title,
        folder_id: folderId
      });
      
      setState(prev => ({
        ...prev,
        documents: [document, ...prev.documents]
      }));
      
      return document;
    } catch (error) {
      setState(prev => ({
        ...prev,
        error: error instanceof Error ? error.message : 'Failed to create document from template'
      }));
      throw error;
    }
  }, []);

  // Auto-save and content management
  const setCurrentDocument = useCallback((document: Document | null) => {
    setState(prev => ({
      ...prev,
      currentDocument: document,
      pendingContent: document?.content || '',
      pendingTitle: document?.title || '',
      hasUnsavedChanges: false
    }));
    
    if (document) {
      lastContentRef.current = document.content;
      lastTitleRef.current = document.title;
    }
  }, []);

  const updateContent = useCallback((content: string) => {
    setState(prev => ({
      ...prev,
      pendingContent: content,
      hasUnsavedChanges: true
    }));
  }, []);

  const updateTitle = useCallback((title: string) => {
    setState(prev => ({
      ...prev,
      pendingTitle: title,
      hasUnsavedChanges: true
    }));
  }, []);

  const saveNow = useCallback(async () => {
    await performAutoSave();
  }, [performAutoSave]);

  // Utility functions
  const getWordCount = useCallback((text: string): number => {
    return text.trim().split(/\s+/).filter(word => word.length > 0).length;
  }, []);

  const getDocumentsByFolder = useCallback((folderId: string): Document[] => {
    return state.documents.filter(doc => doc.folder_id === folderId);
  }, [state.documents]);

  const getRecentDocuments = useCallback((limit: number = 5): Document[] => {
    return [...state.documents]
      .sort((a, b) => new Date(b.updated_at).getTime() - new Date(a.updated_at).getTime())
      .slice(0, limit);
  }, [state.documents]);

  const getTotalWordCount = useCallback((): number => {
    return state.documents.reduce((total, doc) => total + (doc.word_count || 0), 0);
  }, [state.documents]);

  return {
    ...state,
    createDocument,
    getDocument,
    updateDocument,
    deleteDocument,
    duplicateDocument,
    createFolder,
    updateFolder,
    deleteFolder,
    moveDocument,
    searchDocuments,
    clearSearch,
    createFromTemplate,
    setCurrentDocument,
    updateContent,
    updateTitle,
    saveNow,
    getWordCount,
    getDocumentsByFolder,
    getRecentDocuments,
    getTotalWordCount,
    refreshAll
  };
};

 
 