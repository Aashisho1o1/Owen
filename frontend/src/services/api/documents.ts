/**
 * Documents API Service
 * Handles all document-related API calls.
 * Extracted from api.ts as part of God File refactoring.
 */

import apiClient from './client';
import { 
  Document, 
  DocumentsResponse, 
  CreateDocumentRequest, 
  UpdateDocumentRequest,
  CreateFromTemplateRequest 
} from './types';

// === DOCUMENT CRUD OPERATIONS ===

export const getDocuments = async (): Promise<DocumentsResponse> => {
  const response = await apiClient.get('/api/documents');
  return response.data;
};

export const getDocument = async (id: string): Promise<Document> => {
  const response = await apiClient.get(`/api/documents/${id}`);
  return response.data;
};

export const createDocument = async (documentData: CreateDocumentRequest): Promise<Document> => {
  const response = await apiClient.post('/api/documents', documentData);
  return response.data;
};

export const updateDocument = async (id: string, updates: Partial<UpdateDocumentRequest>): Promise<Document> => {
  const response = await apiClient.put(`/api/documents/${id}`, updates);
  return response.data;
};

export const deleteDocument = async (id: string): Promise<void> => {
  await apiClient.delete(`/api/documents/${id}`);
};

export const autoSaveDocument = async (id: string, content: string): Promise<{ status: string; timestamp: string }> => {
  const response = await apiClient.put(`/api/documents/${id}/auto-save`, null, {
    params: { content }
  });
  return response.data;
};

// === TEMPLATE OPERATIONS ===

export const createDocumentFromTemplate = async (templateData: CreateFromTemplateRequest): Promise<Document> => {
  const response = await apiClient.post('/api/documents/from-template', templateData);
  return response.data;
};

// === UTILITY FUNCTIONS ===

export const duplicateDocument = async (id: string, newTitle?: string): Promise<Document> => {
  const updates: any = {};
  if (newTitle) {
    updates.title = newTitle;
  }
  
  // Get the original document first
  const original = await getDocument(id);
  
  // Create a new document with the same content
  const duplicateData: CreateDocumentRequest = {
    title: newTitle || `${original.title} (Copy)`,
    content: original.content || '',
    document_type: original.document_type || 'novel',
    folder_id: original.folder_id
  };
  
  return createDocument(duplicateData);
};

export const moveDocumentToFolder = async (documentId: string, folderId?: string): Promise<Document> => {
  const response = await apiClient.put(`/api/documents/${documentId}`, {
    folder_id: folderId
  });
  return response.data;
}; 
 