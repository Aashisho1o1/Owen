import { useState, useCallback, useEffect, useRef } from 'react';
import api, { Document, CreateDocumentRequest, UpdateDocumentRequest } from '../services/api';
import { logger } from '../utils/logger';
import { useAuth } from '../contexts/AuthContext';

interface UseDocumentsOptions {
  autoSaveDelay?: number; // Time in ms to wait before auto-saving
}

interface UseDocumentsReturn {
  // Document state
  documents: Document[];
  currentDocument: Document | null;
  isLoading: boolean;
  isSaving: boolean;
  error: string | null;
  hasUnsavedChanges: boolean;

  // Document operations
  loadDocuments: () => Promise<void>;
  loadDocument: (id: string) => Promise<void>;
  createDocument: (title: string, content?: string) => Promise<Document | null>;
  saveDocument: (title?: string, content?: string) => Promise<boolean>;
  deleteDocument: (id: string) => Promise<boolean>;
  toggleFavorite: (id: string) => Promise<boolean>;
  
  // Auto-save management
  setCurrentContent: (content: string) => void;
  setCurrentTitle: (title: string) => void;
  clearError: () => void;
  
  // Utility
  getWordCount: (content?: string) => number;
}

export const useDocuments = (options: UseDocumentsOptions = {}): UseDocumentsReturn => {
  const { autoSaveDelay = 2000 } = options;
  const { user, isAuthenticated } = useAuth();
  
  // State
  const [documents, setDocuments] = useState<Document[]>([]);
  const [currentDocument, setCurrentDocument] = useState<Document | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [hasUnsavedChanges, setHasUnsavedChanges] = useState(false);
  
  // Auto-save timer
  const autoSaveTimer = useRef<ReturnType<typeof setTimeout> | null>(null);
  const pendingContent = useRef<string>('');
  const pendingTitle = useRef<string>('');

  // Clear auto-save timer
  const clearAutoSaveTimer = useCallback(() => {
    if (autoSaveTimer.current) {
      clearTimeout(autoSaveTimer.current);
      autoSaveTimer.current = null;
    }
  }, []);

  // Auto-save function
  const triggerAutoSave = useCallback(async () => {
    if (!currentDocument || !hasUnsavedChanges) return;

    try {
      setIsSaving(true);
      const updateData: UpdateDocumentRequest = {
        id: currentDocument.id,
      };

      if (pendingTitle.current !== currentDocument.title) {
        updateData.title = pendingTitle.current;
      }
      
      if (pendingContent.current !== currentDocument.content) {
        updateData.content = pendingContent.current;
      }

      const updatedDoc = await api.updateDocument(updateData);
      
      setCurrentDocument(updatedDoc);
      setHasUnsavedChanges(false);
      setError(null);
      
      // Update in documents list
      setDocuments(prev => 
        prev.map(doc => doc.id === updatedDoc.id ? updatedDoc : doc)
      );
      
      logger.log('Document auto-saved successfully');
    } catch (err) {
      logger.error('Auto-save failed:', err);
      setError('Failed to auto-save document');
    } finally {
      setIsSaving(false);
    }
  }, [currentDocument, hasUnsavedChanges]);

  // Load all documents
  const loadDocuments = useCallback(async () => {
    if (!isAuthenticated) return;
    
    setIsLoading(true);
    setError(null);
    
    try {
      const response = await api.getDocuments();
      setDocuments(response.documents);
      logger.log('Documents loaded successfully', { count: response.documents.length });
    } catch (err) {
      logger.error('Failed to load documents:', err);
      setError('Failed to load documents');
    } finally {
      setIsLoading(false);
    }
  }, [isAuthenticated]);

  // Load a specific document
  const loadDocument = useCallback(async (id: string) => {
    setIsLoading(true);
    setError(null);
    
    try {
      const document = await api.getDocument(id);
      setCurrentDocument(document);
      pendingContent.current = document.content;
      pendingTitle.current = document.title;
      setHasUnsavedChanges(false);
      logger.log('Document loaded successfully', { id, title: document.title });
    } catch (err) {
      logger.error('Failed to load document:', err);
      setError('Failed to load document');
    } finally {
      setIsLoading(false);
    }
  }, []);

  // Create a new document
  const createDocument = useCallback(async (title: string, content = ''): Promise<Document | null> => {
    setIsLoading(true);
    setError(null);
    
    try {
      const request: CreateDocumentRequest = { title, content };
      const newDoc = await api.createDocument(request);
      
      setDocuments(prev => [newDoc, ...prev]);
      setCurrentDocument(newDoc);
      pendingContent.current = content;
      pendingTitle.current = title;
      setHasUnsavedChanges(false);
      
      logger.log('Document created successfully', { id: newDoc.id, title });
      return newDoc;
    } catch (err) {
      logger.error('Failed to create document:', err);
      setError('Failed to create document');
      return null;
    } finally {
      setIsLoading(false);
    }
  }, []);

  // Manual save
  const saveDocument = useCallback(async (title?: string, content?: string): Promise<boolean> => {
    if (!currentDocument) return false;
    
    setIsSaving(true);
    setError(null);
    
    try {
      const updateData: UpdateDocumentRequest = {
        id: currentDocument.id,
      };
      
      if (title !== undefined) {
        updateData.title = title;
        pendingTitle.current = title;
      }
      
      if (content !== undefined) {
        updateData.content = content;
        pendingContent.current = content;
      }

      const updatedDoc = await api.updateDocument(updateData);
      
      setCurrentDocument(updatedDoc);
      setHasUnsavedChanges(false);
      
      // Update in documents list
      setDocuments(prev => 
        prev.map(doc => doc.id === updatedDoc.id ? updatedDoc : doc)
      );
      
      logger.log('Document saved successfully');
      return true;
    } catch (err) {
      logger.error('Failed to save document:', err);
      setError('Failed to save document');
      return false;
    } finally {
      setIsSaving(false);
    }
  }, [currentDocument]);

  // Delete document
  const deleteDocument = useCallback(async (id: string): Promise<boolean> => {
    setError(null);
    
    try {
      await api.deleteDocument(id);
      
      setDocuments(prev => prev.filter(doc => doc.id !== id));
      
      if (currentDocument?.id === id) {
        setCurrentDocument(null);
        setHasUnsavedChanges(false);
      }
      
      logger.log('Document deleted successfully', { id });
      return true;
    } catch (err) {
      logger.error('Failed to delete document:', err);
      setError('Failed to delete document');
      return false;
    }
  }, [currentDocument]);

  // Toggle favorite status
  const toggleFavorite = useCallback(async (id: string): Promise<boolean> => {
    const document = documents.find(doc => doc.id === id);
    if (!document) return false;
    
    try {
      const updateData: UpdateDocumentRequest = {
        id,
        is_favorite: !document.is_favorite,
      };
      
      const updatedDoc = await api.updateDocument(updateData);
      
      setDocuments(prev => 
        prev.map(doc => doc.id === id ? updatedDoc : doc)
      );
      
      if (currentDocument?.id === id) {
        setCurrentDocument(updatedDoc);
      }
      
      return true;
    } catch (err) {
      logger.error('Failed to toggle favorite:', err);
      setError('Failed to update favorite status');
      return false;
    }
  }, [documents, currentDocument]);

  // Set current content with auto-save
  const setCurrentContent = useCallback((content: string) => {
    if (!currentDocument) return;
    
    pendingContent.current = content;
    setHasUnsavedChanges(content !== currentDocument.content || pendingTitle.current !== currentDocument.title);
    
    // Clear existing timer and set new one
    clearAutoSaveTimer();
    autoSaveTimer.current = setTimeout(triggerAutoSave, autoSaveDelay);
  }, [currentDocument, clearAutoSaveTimer, triggerAutoSave, autoSaveDelay]);

  // Set current title with auto-save
  const setCurrentTitle = useCallback((title: string) => {
    if (!currentDocument) return;
    
    pendingTitle.current = title;
    setHasUnsavedChanges(title !== currentDocument.title || pendingContent.current !== currentDocument.content);
    
    // Clear existing timer and set new one
    clearAutoSaveTimer();
    autoSaveTimer.current = setTimeout(triggerAutoSave, autoSaveDelay);
  }, [currentDocument, clearAutoSaveTimer, triggerAutoSave, autoSaveDelay]);

  // Clear error
  const clearError = useCallback(() => {
    setError(null);
  }, []);

  // Word count utility
  const getWordCount = useCallback((content?: string) => {
    if (!content) return 0;
    return content.trim().split(/\s+/).filter(word => word.length > 0).length;
  }, []);

  // Load documents when user authentication changes
  useEffect(() => {
    if (isAuthenticated && user) {
      loadDocuments();
    } else {
      setDocuments([]);
      setCurrentDocument(null);
      setHasUnsavedChanges(false);
    }
  }, [isAuthenticated, user, loadDocuments]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      clearAutoSaveTimer();
    };
  }, [clearAutoSaveTimer]);

  return {
    // State
    documents,
    currentDocument,
    isLoading,
    isSaving,
    error,
    hasUnsavedChanges,
    
    // Operations
    loadDocuments,
    loadDocument,
    createDocument,
    saveDocument,
    deleteDocument,
    toggleFavorite,
    
    // Content management
    setCurrentContent,
    setCurrentTitle,
    clearError,
    
    // Utility
    getWordCount,
  };
}; 