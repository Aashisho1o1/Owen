/**
 * Documents API Service
 * Handles all document-related API calls.
 * Extracted from api.ts as part of God File refactoring.
 */

import { apiClient, safeApiCall } from './client';
import { 
  Document, 
  DocumentsResponse, 
  CreateDocumentRequest, 
  UpdateDocumentRequest,
  CreateFromTemplateRequest 
} from './types';

// === DOCUMENT CRUD OPERATIONS ===

export const getDocuments = async (): Promise<DocumentsResponse> => {
  return safeApiCall(async () => {
    const response = await apiClient.get('/api/documents');
    return response.data;
  });
};

export const getDocument = async (id: string): Promise<Document> => {
  return safeApiCall(async () => {
    const response = await apiClient.get(`/api/documents/${id}`);
    return response.data;
  });
};

export const createDocument = async (documentData: CreateDocumentRequest): Promise<Document> => {
  return safeApiCall(async () => {
    const response = await apiClient.post('/api/documents', documentData);
    return response.data;
  });
};

export const updateDocument = async (id: string, updates: Partial<UpdateDocumentRequest>): Promise<Document> => {
  return safeApiCall(async () => {
    const response = await apiClient.put(`/api/documents/${id}`, updates);
    return response.data;
  });
};

export const deleteDocument = async (id: string): Promise<void> => {
  return safeApiCall(async () => {
    await apiClient.delete(`/api/documents/${id}`);
  });
};

export const autoSaveDocument = async (id: string, content: string): Promise<{ status: string; timestamp: string }> => {
  return safeApiCall(async () => {
    const response = await apiClient.put(`/api/documents/${id}/auto-save?content=${encodeURIComponent(content)}`);
    return response.data;
  });
};

// === TEMPLATE OPERATIONS ===

export const createDocumentFromTemplate = async (templateData: CreateFromTemplateRequest): Promise<Document> => {
  return safeApiCall(async () => {
    const response = await apiClient.post('/api/documents/from-template', templateData);
    return response.data;
  });
};

// === UTILITY FUNCTIONS ===

export const duplicateDocument = async (id: string, newTitle?: string): Promise<Document> => {
  return safeApiCall(async () => {
    // Get the original document
    const original = await getDocument(id);
    
    // Create a copy with modified title
    const duplicateData: CreateDocumentRequest = {
      title: newTitle || `${original.title} (Copy)`,
      content: original.content,
      document_type: original.document_type,
      folder_id: original.folder_id
    };
    
    return await createDocument(duplicateData);
  });
};

export const moveDocumentToFolder = async (documentId: string, folderId?: string): Promise<Document> => {
  return updateDocument(documentId, { folder_id: folderId });
}; 
 