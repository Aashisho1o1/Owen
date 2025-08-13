import { useState, useEffect, useCallback, useRef } from 'react';
import { useAuth } from '../contexts/AuthContext';
import * as api from '../services/api';
import { 
  Document, 
  DocumentFolder, 
  SearchRequest,
  SearchResult
} from '../services/api';

interface ApiError extends Error {
  response?: {
    data?: {
      detail?: string;
    };
  };
}

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
  const { user, isLoading: isAuthLoading } = useAuth();
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
      const apiError = error as ApiError;
      setState(prev => ({ 
        ...prev, 
        isSaving: false, 
        error: apiError.response?.data?.detail || apiError.message || 'Failed to save document' 
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

  // FIXED: Add request deduplication to prevent duplicate API calls
  const fetchInProgress = useRef(false);
  const lastUserId = useRef<string | null>(null);

  // Fetch initial data (documents and folders)
  const fetchAllData = useCallback(async () => {
    // SAFETY: Wait for authentication to complete before making API calls
    if (isAuthLoading) {
      console.log('🔄 useDocuments: Authentication still loading, skipping data load');
      return;
    }
    
    if (!user) {
      console.log('🔐 useDocuments: No user, skipping data load');
      // Clear any existing data when user logs out
      setState(prev => ({
        ...prev,
        documents: [],
        folders: [],
        currentDocument: null,
        isLoading: false,
        error: null
      }));
      return;
    }

    // FIXED: Prevent duplicate requests for same user
    const currentUserId = user.user_id;
    if (fetchInProgress.current) {
      console.log('🔄 useDocuments: Request already in progress, skipping');
      return;
    }

    if (lastUserId.current === currentUserId && state.documents.length > 0) {
      console.log('📊 useDocuments: Data already loaded for current user');
      return;
    }

    fetchInProgress.current = true;
    lastUserId.current = currentUserId;
    
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
    } catch (err) {
      const apiError = err as ApiError;
      console.error('❌ useDocuments: Error fetching initial data', {
        message: apiError.response?.data?.detail || apiError.message,
        stack: apiError.stack,
      });
      
      // FIXED: Handle rate limiting gracefully
      if (apiError.message?.includes('429') || apiError.message?.includes('rate limit') || apiError.message?.includes('too many requests')) {
        console.log('⏱️ useDocuments: Rate limited, will retry in 5 seconds');
        setState(prev => ({
          ...prev,
          error: 'Too many requests. Retrying in 5 seconds...',
          isLoading: false
        }));
        
        // Retry after 5 seconds
        setTimeout(() => {
          fetchInProgress.current = false;
          fetchAllData();
        }, 5000);
      } else {
        setState(prev => ({
          ...prev,
          isLoading: false,
          error: apiError.response?.data?.detail || apiError.message || 'Failed to load documents.',
          documents: [],
          folders: []
        }));
      }
    } finally {
      fetchInProgress.current = false;
    }
  }, [user, state.documents.length, isAuthLoading]);

  useEffect(() => {
    // CRITICAL FIX: Only fetch data after auth initialization completes
    // This prevents premature API calls that trigger 403 → logout loops
    if (!isAuthLoading) {
      fetchAllData();
    } else {
      console.log('🔄 useDocuments: Waiting for auth initialization to complete...');
    }
  }, [fetchAllData, isAuthLoading]);

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
      const apiError = error as ApiError;
      setState(prev => ({
        ...prev,
        error: apiError.response?.data?.detail || apiError.message || 'Failed to create document',
        isLoading: false
      }));
      throw apiError;
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
    } catch (err) {
      const apiError = err as ApiError;
      console.error(`❌ useDocuments: Error fetching document ${id}`, err);
      setState(prev => ({ ...prev, error: apiError.response?.data?.detail || apiError.message || 'Failed to fetch document.' }));
      throw apiError;
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
      const apiError = error as ApiError;
      setState(prev => ({
        ...prev,
        error: apiError.response?.data?.detail || apiError.message || 'Failed to update document'
      }));
      throw apiError;
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
      const apiError = error as ApiError;
      setState(prev => ({
        ...prev,
        error: apiError.response?.data?.detail || apiError.message || 'Failed to delete document'
      }));
      throw apiError;
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
      const apiError = error as ApiError;
      setState(prev => ({
        ...prev,
        error: apiError.response?.data?.detail || apiError.message || 'Failed to duplicate document'
      }));
      throw apiError;
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
    } catch (err) {
      const apiError = err as ApiError;
      console.error('❌ useDocuments: Error creating folder', err);
      setState(prev => ({ ...prev, error: apiError.response?.data?.detail || apiError.message || 'Failed to create folder.' }));
      throw apiError;
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
    } catch (err) {
      const apiError = err as ApiError;
      console.error(`❌ useDocuments: Error updating folder ${id}`, err);
      setState(prev => ({ ...prev, error: apiError.response?.data?.detail || apiError.message || 'Failed to update folder.' }));
      throw apiError;
    }
  };

  const deleteFolder = async (id: string) => {
    try {
      await api.deleteFolder(id);
      
      // Optimistically update UI
      setState(prev => ({
        ...prev,
        folders: prev.folders.filter(f => f.id !== id),
      }));
    } catch (err) {
      const apiError = err as ApiError;
      console.error(`❌ useDocuments: Error deleting folder ${id}`, err);
      setState(prev => ({ ...prev, error: apiError.response?.data?.detail || apiError.message || 'Failed to delete folder.' }));
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
    } catch (err) {
      const apiError = err as ApiError;
      console.error(`❌ useDocuments: Error moving document ${documentId}`, err);
      setState(prev => ({ ...prev, error: apiError.response?.data?.detail || apiError.message || 'Failed to move document.' }));
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
    } catch (err) {
      const apiError = err as ApiError;
      console.error('❌ useDocuments: Error searching documents', err);
      setState(prev => ({
        ...prev,
        isSearching: false,
        error: apiError.response?.data?.detail || apiError.message || 'Failed to search documents.',
      }));
    }
  };

  const clearSearch = () => {
    setState(prev => ({ ...prev, searchResults: [], isSearching: false }));
  };

  // Auto-save & sync
  const setCurrentDocument = (doc: Document | null) => {
    console.log('📋 useDocuments: Setting current document:', {
      newDocId: doc?.id || 'null',
      newDocTitle: doc?.title || 'null',
      previousDocId: state.currentDocument?.id || 'null',
      previousDocTitle: state.currentDocument?.title || 'null',
      hasUnsavedChanges: state.hasUnsavedChanges
    });
    
    if (state.currentDocument && state.hasUnsavedChanges) {
      console.log('💾 useDocuments: Auto-saving previous document before switching');
      saveNow();
    }
    
    // CRITICAL FIX: Don't overwrite content if user has unsaved changes for the same document
    const isUpdatingSameDocument = doc && state.currentDocument && doc.id === state.currentDocument.id;
    const shouldPreserveContent = isUpdatingSameDocument && state.hasUnsavedChanges;
    
    setState(prev => ({
      ...prev,
      currentDocument: doc,
      // Preserve user content if they have unsaved changes to the same document
      pendingContent: shouldPreserveContent ? prev.pendingContent : (doc?.content || ''),
      pendingTitle: shouldPreserveContent ? prev.pendingTitle : (doc?.title || ''),
      hasUnsavedChanges: shouldPreserveContent ? prev.hasUnsavedChanges : false
    }));
    
    if (doc && !shouldPreserveContent) {
      lastContentRef.current = doc.content;
      lastTitleRef.current = doc.title;
    }
    
    console.log('✅ useDocuments: Current document set successfully');
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
    
    console.log('💾 useDocuments: Saving document:', {
      documentId: state.currentDocument.id,
      title: state.currentDocument.title,
      pendingContent: state.pendingContent.substring(0, 100) + '...',
      pendingContentLength: state.pendingContent.length
    });
    
    try {
      const updates: Partial<Document> = {
        content: state.pendingContent,
        title: state.pendingTitle,
      };

      const updatedDocument = await api.updateDocument(state.currentDocument.id, updates);
      
      console.log('✅ useDocuments: Document saved successfully:', {
        documentId: updatedDocument.id,
        title: updatedDocument.title,
        wordCount: updatedDocument.word_count
      });
      
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
    } catch (err) {
      const apiError = err as ApiError;
      console.error(`❌ useDocuments: Error saving document ${state.currentDocument.id}`, err);
      setState(prev => ({
        ...prev,
        isSaving: false,
        error: apiError.response?.data?.detail || apiError.message || 'Failed to save document.',
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

 
 