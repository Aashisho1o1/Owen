import { useState, useEffect, useCallback, useRef } from 'react';
import api, { 
  Document, 
  DocumentVersion, 
  DocumentFolder, 
  DocumentSeries, 
  DocumentTemplate,
  WritingGoal,
  WritingSession,
  SearchRequest,
  SearchResult,
  ExportRequest
} from '../services/api';
import { useAuth } from '../contexts/AuthContext';

interface DocumentState {
  documents: Document[];
  folders: DocumentFolder[];
  series: DocumentSeries[];
  templates: DocumentTemplate[];
  writingGoals: WritingGoal[];
  currentDocument: Document | null;
  isLoading: boolean;
  error: string | null;
  
  // Version management
  versions: DocumentVersion[];
  isLoadingVersions: boolean;
  
  // Search
  searchResults: SearchResult[];
  isSearching: boolean;
  
  // Analytics
  writingStats: any;
  writingSessions: WritingSession[];
  
  // Auto-save
  isSaving: boolean;
  lastSaved: Date | null;
  hasUnsavedChanges: boolean;
  pendingContent: string;
  pendingTitle: string;
}

interface UseDocumentsReturn extends DocumentState {
  // Document CRUD
  createDocument: (title: string, documentType?: string, folderId?: string, seriesId?: string) => Promise<Document>;
  getDocument: (id: string) => Promise<Document>;
  updateDocument: (id: string, updates: Partial<Document>) => Promise<Document>;
  deleteDocument: (id: string) => Promise<void>;
  duplicateDocument: (id: string, newTitle?: string) => Promise<Document>;
  
  // Version management
  loadVersions: (documentId: string) => Promise<void>;
  restoreVersion: (documentId: string, versionId: string) => Promise<void>;
  compareVersions: (documentId: string, v1: string, v2: string) => Promise<any>;
  
  // Folder management
  createFolder: (name: string, parentId?: string, color?: string) => Promise<DocumentFolder>;
  updateFolder: (id: string, updates: Partial<DocumentFolder>) => Promise<DocumentFolder>;
  deleteFolder: (id: string, moveDocumentsTo?: string) => Promise<void>;
  moveDocument: (documentId: string, folderId?: string, seriesId?: string) => Promise<void>;
  
  // Series management
  createSeries: (name: string, description?: string) => Promise<DocumentSeries>;
  updateSeries: (id: string, updates: Partial<DocumentSeries>) => Promise<DocumentSeries>;
  deleteSeries: (id: string) => Promise<void>;
  
  // Search
  searchDocuments: (searchRequest: SearchRequest) => Promise<void>;
  clearSearch: () => void;
  
  // Templates
  createFromTemplate: (templateId: string, title: string, folderId?: string) => Promise<Document>;
  
  // Export
  exportDocument: (documentId: string, format: string, options?: any) => Promise<void>;
  
  // Writing goals & analytics
  createWritingGoal: (goal: Omit<WritingGoal, 'id' | 'user_id' | 'current_words'>) => Promise<WritingGoal>;
  loadWritingStats: (period: 'week' | 'month' | 'year') => Promise<void>;
  loadWritingSessions: (documentId?: string, dateRange?: { start: string; end: string }) => Promise<void>;
  
  // Auto-save & sync
  setCurrentDocument: (document: Document | null) => void;
  updateContent: (content: string) => void;
  updateTitle: (title: string) => void;
  saveNow: () => Promise<void>;
  
  // Backup
  createBackup: () => Promise<{ backup_id: string; download_url: string }>;
  
  // Collaboration
  shareDocument: (documentId: string, email: string, permission: 'view' | 'comment' | 'edit') => Promise<void>;
  
  // Utility functions
  getWordCount: (text: string) => number;
  getDocumentsByFolder: (folderId: string) => Document[];
  getDocumentsBySeries: (seriesId: string) => Document[];
  getFolderTree: () => DocumentFolder[];
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
    series: [],
    templates: [],
    writingGoals: [],
    currentDocument: null,
    isLoading: false,
    error: null,
    versions: [],
    isLoadingVersions: false,
    searchResults: [],
    isSearching: false,
    writingStats: null,
    writingSessions: [],
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

  // Load initial data
  const refreshAll = useCallback(async () => {
    if (!user) return;
    
    setState(prev => ({ ...prev, isLoading: true, error: null }));
    
    try {
      const [documents, folders, series, templates, goals] = await Promise.all([
        api.getDocuments(),
        api.getFolders(),
        api.getSeries(),
        api.getTemplates(),
        api.getWritingGoals()
      ]);
      
      setState(prev => ({
        ...prev,
        documents: documents.documents || [],
        folders,
        series,
        templates,
        writingGoals: goals,
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

  // Document CRUD operations
  const createDocument = useCallback(async (
    title: string, 
    documentType: string = 'novel', 
    folderId?: string, 
    seriesId?: string
  ): Promise<Document> => {
    try {
      setState(prev => ({ ...prev, isLoading: true }));
      
      const document = await api.createDocument({
        title,
        content: '',
        document_type: documentType as any,
        folder_id: folderId,
        series_id: seriesId
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
      setState(prev => ({
        ...prev,
        documents: prev.documents.map(doc => doc.id === id ? document : doc)
      }));
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
      const document = await api.updateDocument(id, updates);
      setState(prev => ({
        ...prev,
        documents: prev.documents.map(doc => doc.id === id ? document : doc),
        currentDocument: prev.currentDocument?.id === id ? document : prev.currentDocument
      }));
      return document;
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
      const document = await api.duplicateDocument(id, newTitle);
      setState(prev => ({
        ...prev,
        documents: [document, ...prev.documents]
      }));
      return document;
    } catch (error) {
      setState(prev => ({ 
        ...prev, 
        error: error instanceof Error ? error.message : 'Failed to duplicate document' 
      }));
      throw error;
    }
  }, []);

  // Version management
  const loadVersions = useCallback(async (documentId: string): Promise<void> => {
    try {
      setState(prev => ({ ...prev, isLoadingVersions: true }));
      const versions = await api.getDocumentVersions(documentId);
      setState(prev => ({ ...prev, versions, isLoadingVersions: false }));
    } catch (error) {
      setState(prev => ({ 
        ...prev, 
        error: error instanceof Error ? error.message : 'Failed to load versions',
        isLoadingVersions: false 
      }));
    }
  }, []);

  const restoreVersion = useCallback(async (documentId: string, versionId: string): Promise<void> => {
    try {
      const document = await api.restoreDocumentVersion(documentId, versionId);
      setState(prev => ({
        ...prev,
        documents: prev.documents.map(doc => doc.id === documentId ? document : doc),
        currentDocument: prev.currentDocument?.id === documentId ? document : prev.currentDocument
      }));
    } catch (error) {
      setState(prev => ({ 
        ...prev, 
        error: error instanceof Error ? error.message : 'Failed to restore version' 
      }));
      throw error;
    }
  }, []);

  const compareVersions = useCallback(async (documentId: string, v1: string, v2: string): Promise<any> => {
    try {
      return await api.compareVersions(documentId, v1, v2);
    } catch (error) {
      setState(prev => ({ 
        ...prev, 
        error: error instanceof Error ? error.message : 'Failed to compare versions' 
      }));
      throw error;
    }
  }, []);

  // Folder management
  const createFolder = useCallback(async (name: string, parentId?: string, color?: string): Promise<DocumentFolder> => {
    try {
      const folder = await api.createFolder(name, parentId, color);
      setState(prev => ({ ...prev, folders: [...prev.folders, folder] }));
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
      const folder = await api.updateFolder(id, updates);
      setState(prev => ({
        ...prev,
        folders: prev.folders.map(f => f.id === id ? folder : f)
      }));
      return folder;
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
      await api.deleteFolder(id, moveDocumentsTo);
      setState(prev => ({
        ...prev,
        folders: prev.folders.filter(f => f.id !== id)
      }));
      // Refresh documents to update folder assignments
      await refreshAll();
    } catch (error) {
      setState(prev => ({ 
        ...prev, 
        error: error instanceof Error ? error.message : 'Failed to delete folder' 
      }));
      throw error;
    }
  }, [refreshAll]);

  const moveDocument = useCallback(async (documentId: string, folderId?: string, seriesId?: string): Promise<void> => {
    try {
      const document = await api.moveDocument(documentId, folderId, seriesId);
      setState(prev => ({
        ...prev,
        documents: prev.documents.map(doc => doc.id === documentId ? document : doc)
      }));
    } catch (error) {
      setState(prev => ({ 
        ...prev, 
        error: error instanceof Error ? error.message : 'Failed to move document' 
      }));
      throw error;
    }
  }, []);

  // Series management
  const createSeries = useCallback(async (name: string, description?: string): Promise<DocumentSeries> => {
    try {
      const series = await api.createSeries(name, description);
      setState(prev => ({ ...prev, series: [...prev.series, series] }));
      return series;
    } catch (error) {
      setState(prev => ({ 
        ...prev, 
        error: error instanceof Error ? error.message : 'Failed to create series' 
      }));
      throw error;
    }
  }, []);

  const updateSeries = useCallback(async (id: string, updates: Partial<DocumentSeries>): Promise<DocumentSeries> => {
    try {
      const series = await api.updateSeries(id, updates);
      setState(prev => ({
        ...prev,
        series: prev.series.map(s => s.id === id ? series : s)
      }));
      return series;
    } catch (error) {
      setState(prev => ({ 
        ...prev, 
        error: error instanceof Error ? error.message : 'Failed to update series' 
      }));
      throw error;
    }
  }, []);

  const deleteSeries = useCallback(async (id: string): Promise<void> => {
    try {
      await api.deleteSeries(id);
      setState(prev => ({
        ...prev,
        series: prev.series.filter(s => s.id !== id)
      }));
      // Refresh documents to update series assignments
      await refreshAll();
    } catch (error) {
      setState(prev => ({ 
        ...prev, 
        error: error instanceof Error ? error.message : 'Failed to delete series' 
      }));
      throw error;
    }
  }, [refreshAll]);

  // Search
  const searchDocuments = useCallback(async (searchRequest: SearchRequest): Promise<void> => {
    try {
      setState(prev => ({ ...prev, isSearching: true }));
      const results = await api.searchDocuments(searchRequest);
      setState(prev => ({ ...prev, searchResults: results, isSearching: false }));
    } catch (error) {
      setState(prev => ({ 
        ...prev, 
        error: error instanceof Error ? error.message : 'Failed to search documents',
        isSearching: false 
      }));
    }
  }, []);

  const clearSearch = useCallback(() => {
    setState(prev => ({ ...prev, searchResults: [] }));
  }, []);

  // Templates
  const createFromTemplate = useCallback(async (templateId: string, title: string, folderId?: string): Promise<Document> => {
    try {
      const document = await api.createDocumentFromTemplate(templateId, title, folderId);
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

  // Export
  const exportDocument = useCallback(async (documentId: string, format: string, options?: any): Promise<void> => {
    try {
      const blob = await api.exportDocument({
        document_id: documentId,
        format: format as any,
        ...options
      });
      
      // Create download link
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `document.${format}`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (error) {
      setState(prev => ({ 
        ...prev, 
        error: error instanceof Error ? error.message : 'Failed to export document' 
      }));
      throw error;
    }
  }, []);

  // Writing goals & analytics
  const createWritingGoal = useCallback(async (goal: Omit<WritingGoal, 'id' | 'user_id' | 'current_words'>): Promise<WritingGoal> => {
    try {
      const newGoal = await api.createWritingGoal(goal);
      setState(prev => ({ ...prev, writingGoals: [...prev.writingGoals, newGoal] }));
      return newGoal;
    } catch (error) {
      setState(prev => ({ 
        ...prev, 
        error: error instanceof Error ? error.message : 'Failed to create writing goal' 
      }));
      throw error;
    }
  }, []);

  const loadWritingStats = useCallback(async (period: 'week' | 'month' | 'year'): Promise<void> => {
    try {
      const stats = await api.getWritingStats(period);
      setState(prev => ({ ...prev, writingStats: stats }));
    } catch (error) {
      setState(prev => ({ 
        ...prev, 
        error: error instanceof Error ? error.message : 'Failed to load writing stats' 
      }));
    }
  }, []);

  const loadWritingSessions = useCallback(async (documentId?: string, dateRange?: { start: string; end: string }): Promise<void> => {
    try {
      const sessions = await api.getWritingSessions(documentId, dateRange);
      setState(prev => ({ ...prev, writingSessions: sessions }));
    } catch (error) {
      setState(prev => ({ 
        ...prev, 
        error: error instanceof Error ? error.message : 'Failed to load writing sessions' 
      }));
    }
  }, []);

  // Auto-save & sync
  const setCurrentDocument = useCallback((document: Document | null) => {
    // Save any pending changes before switching
    if (state.hasUnsavedChanges && state.currentDocument) {
      performAutoSave();
    }
    
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
  }, [state.hasUnsavedChanges, state.currentDocument, performAutoSave]);

  const updateContent = useCallback((content: string) => {
    setState(prev => ({
      ...prev,
      pendingContent: content,
      hasUnsavedChanges: content !== lastContentRef.current || prev.pendingTitle !== lastTitleRef.current
    }));
  }, []);

  const updateTitle = useCallback((title: string) => {
    setState(prev => ({
      ...prev,
      pendingTitle: title,
      hasUnsavedChanges: title !== lastTitleRef.current || prev.pendingContent !== lastContentRef.current
    }));
  }, []);

  const saveNow = useCallback(async (): Promise<void> => {
    await performAutoSave();
  }, [performAutoSave]);

  // Backup
  const createBackup = useCallback(async (): Promise<{ backup_id: string; download_url: string }> => {
    try {
      return await api.createBackup();
    } catch (error) {
      setState(prev => ({ 
        ...prev, 
        error: error instanceof Error ? error.message : 'Failed to create backup' 
      }));
      throw error;
    }
  }, []);

  // Collaboration
  const shareDocument = useCallback(async (documentId: string, email: string, permission: 'view' | 'comment' | 'edit'): Promise<void> => {
    try {
      await api.shareDocument(documentId, email, permission);
    } catch (error) {
      setState(prev => ({ 
        ...prev, 
        error: error instanceof Error ? error.message : 'Failed to share document' 
      }));
      throw error;
    }
  }, []);

  // Utility functions
  const getWordCount = useCallback((text: string): number => {
    return text.trim().split(/\s+/).filter(word => word.length > 0).length;
  }, []);

  const getDocumentsByFolder = useCallback((folderId: string): Document[] => {
    return state.documents.filter(doc => doc.folder_id === folderId);
  }, [state.documents]);

  const getDocumentsBySeries = useCallback((seriesId: string): Document[] => {
    return state.documents.filter(doc => doc.series_id === seriesId)
      .sort((a, b) => (a.chapter_number || 0) - (b.chapter_number || 0));
  }, [state.documents]);

  const getFolderTree = useCallback((): DocumentFolder[] => {
    const buildTree = (parentId?: string): DocumentFolder[] => {
      return state.folders
        .filter(folder => folder.parent_id === parentId)
        .map(folder => ({
          ...folder,
          children: buildTree(folder.id)
        }));
    };
    return buildTree();
  }, [state.folders]);

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
    loadVersions,
    restoreVersion,
    compareVersions,
    createFolder,
    updateFolder,
    deleteFolder,
    moveDocument,
    createSeries,
    updateSeries,
    deleteSeries,
    searchDocuments,
    clearSearch,
    createFromTemplate,
    exportDocument,
    createWritingGoal,
    loadWritingStats,
    loadWritingSessions,
    setCurrentDocument,
    updateContent,
    updateTitle,
    saveNow,
    createBackup,
    shareDocument,
    getWordCount,
    getDocumentsByFolder,
    getDocumentsBySeries,
    getFolderTree,
    getRecentDocuments,
    getTotalWordCount,
    refreshAll,
  };
};
