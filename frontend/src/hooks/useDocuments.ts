import { useState, useEffect, useCallback, useRef } from 'react';
import { useAuth } from '../contexts/AuthContext';
import * as api from '../services/api';
import { 
  Document, 
  DocumentFolder, 
  SearchRequest,
  SearchResult
} from '../services/api';

// MVP-focused DocumentState - removed analytics, versions, series, goals
interface DocumentState {
  documents: Document[];
  folders: DocumentFolder[];
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
  
  // Auto-save & sync
  setCurrentDocument: (document: Document | null) => void;
  updateContent: (content: string) => void;
  updateTitle: (title: string) => void;
  saveNow: () => Promise<void>;
  
  // Utility functions
  getWordCount: (text: string) => number;
  getDocumentsByFolder: (folderId: string) => Document[];
  getTotalWordCount: () => number;
  
  // Refresh data
  refreshAll: () => Promise<void>;
}

export const useDocuments = (): UseDocumentsReturn => {
  const { user } = useAuth();
  const [state, setState] = useState<DocumentState>({
    documents: [],
    folders: [],
    currentDocument: null,
    isLoading: true,
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

  // Fetch initial data (documents and folders)
  const fetchAllData = useCallback(async () => {
    setState(prev => ({ ...prev, isLoading: true }));
    try {
      const [docsResponse, foldersResponse] = await Promise.all([
        api.getDocuments(),
        api.getFolders()
      ]);
      
      const documents = docsResponse.documents || [];
      const folders = foldersResponse || [];

      console.log(
        `📊 useDocuments: Loaded ${documents.length} documents and ${folders.length} folders.`
      );

      setState(prev => ({
        ...prev,
        documents,
        folders,
        isLoading: false,
        error: null,
      }));
    } catch (err: any) {
      console.error('❌ useDocuments: Error fetching initial data', {
        message: err.message,
        stack: err.stack,
      });
      setState(prev => ({
        ...prev,
        isLoading: false,
        error: err.message || 'Failed to load documents.',
        documents: [],
        folders: []
      }));
    }
  }, []);

  useEffect(() => {
    fetchAllData();
  }, [fetchAllData]);

  // Document CRUD operations
  const createDocument = async (
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
        documents: [...state.documents, document],
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
  };

  const getDocument = async (id: string): Promise<Document> => {
    try {
      const doc = await api.getDocument(id);
      setState(prev => ({
        ...prev,
        documents: prev.documents.map(d => (d.id === id ? doc : d)),
      }));
      return doc;
    } catch (err: any) {
      console.error(`❌ useDocuments: Error fetching document ${id}`, err);
      setState(prev => ({ ...prev, error: err.message || 'Failed to fetch document.' }));
      throw err;
    }
  };

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
  const createFolder = async (
    name: string,
    parentId?: string,
    color?: string
  ): Promise<DocumentFolder> => {
    try {
      const folder = await api.createFolder({ name, parent_id: parentId, color });
      
      setState(prev => ({
        ...prev,
        folders: [...prev.folders, folder]
      }));
      
      return folder;
    } catch (err: any) {
      console.error('❌ useDocuments: Error creating folder', err);
      setState(prev => ({ ...prev, error: err.message || 'Failed to create folder.' }));
      throw err;
    }
  };

  const updateFolder = async (
    id: string,
    updates: Partial<DocumentFolder>
  ): Promise<DocumentFolder> => {
    try {
      const updatedFolder = await api.updateFolder(id, updates);
      
      setState(prev => ({
        ...prev,
        folders: prev.folders.map(folder => 
          folder.id === id ? updatedFolder : folder
        )
      }));
      
      return updatedFolder;
    } catch (err: any) {
      console.error(`❌ useDocuments: Error updating folder ${id}`, err);
      setState(prev => ({ ...prev, error: err.message || 'Failed to update folder.' }));
      throw err;
    }
  };

  const deleteFolder = async (id: string, moveDocumentsTo?: string) => {
    try {
      await api.deleteFolder(id);
      
      // Optimistically update UI
      setState(prev => ({
        ...prev,
        folders: prev.folders.filter(f => f.id !== id),
      }));
    } catch (err: any) {
      console.error(`❌ useDocuments: Error deleting folder ${id}`, err);
      setState(prev => ({ ...prev, error: err.message || 'Failed to delete folder.' }));
      // NOTE: Consider reverting optimistic update on failure
    }
  };

  const moveDocument = async (documentId: string, folderId?: string) => {
    try {
      const updatedDoc = await api.moveDocumentToFolder(documentId, folderId);
      setState(prev => ({
        ...prev,
        documents: prev.documents.map(d => (d.id === documentId ? updatedDoc : d)),
      }));
    } catch (err: any) {
      console.error(`❌ useDocuments: Error moving document ${documentId}`, err);
      setState(prev => ({ ...prev, error: err.message || 'Failed to move document.' }));
    }
  };


  // Search
  const searchDocuments = async (searchRequest: SearchRequest) => {
    setState(prev => ({ ...prev, isSearching: true, error: null }));
    try {
      const results = await api.searchDocuments(searchRequest);
      setState(prev => ({
        ...prev,
        searchResults: results,
        isSearching: false,
      }));
    } catch (err: any) {
      console.error('❌ useDocuments: Error searching documents', err);
      setState(prev => ({
        ...prev,
        isSearching: false,
        error: err.message || 'Failed to search documents.',
      }));
    }
  };

  const clearSearch = () => {
    setState(prev => ({ ...prev, searchResults: [], isSearching: false }));
  };

  // Auto-save & sync
  const setCurrentDocument = (doc: Document | null) => {
    if (state.currentDocument && state.hasUnsavedChanges) {
      saveNow();
    }
    
    setState(prev => ({
      ...prev,
      currentDocument: doc,
      pendingContent: doc?.content || '',
      pendingTitle: doc?.title || '',
      hasUnsavedChanges: false
    }));
    
    if (doc) {
      lastContentRef.current = doc.content;
      lastTitleRef.current = doc.title;
    }
  };

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
    if (!state.currentDocument || !state.hasUnsavedChanges) return;

    setState(prev => ({ ...prev, isSaving: true }));
    
    try {
      const updates: Partial<Document> = {
        content: state.pendingContent,
        title: state.pendingTitle,
      };

      const updatedDocument = await api.updateDocument(state.currentDocument.id, updates);
      
      setState(prev => ({
        ...prev,
        isSaving: false,
        lastSaved: new Date(),
        hasUnsavedChanges: false,
        documents: prev.documents.map(doc => 
          doc.id === state.currentDocument?.id ? updatedDocument : doc
        ),
        currentDocument: updatedDocument
      }));
    } catch (err: any) {
      console.error(`❌ useDocuments: Error saving document ${state.currentDocument.id}`, err);
      setState(prev => ({
        ...prev,
        isSaving: false,
        error: err.message || 'Failed to save document.',
      }));
    }
  }, [state.currentDocument, state.pendingContent, state.pendingTitle, state.hasUnsavedChanges]);

  // Utility functions
  const getWordCount = (text: string): number => {
    return text.trim().split(/\s+/).filter(Boolean).length;
  };

  const getDocumentsByFolder = useCallback((folderId: string): Document[] => {
    return state.documents.filter(doc => doc.folder_id === folderId);
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
    setCurrentDocument,
    updateContent,
    updateTitle,
    saveNow,
    getWordCount,
    getDocumentsByFolder,
    getTotalWordCount,
    refreshAll: fetchAllData,
  };
};

 
 