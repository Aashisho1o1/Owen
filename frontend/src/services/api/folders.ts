/**
 * Folders API Service
 * Handles all folder-related API calls.
 * Extracted from api.ts as part of God File refactoring.
 */

import { apiClient, safeApiCall } from './client';
import { DocumentFolder, CreateFolderRequest } from './types';

// === FOLDER CRUD OPERATIONS ===

export const getFolders = async (): Promise<DocumentFolder[]> => {
  return safeApiCall(async () => {
    const response = await apiClient.get('/api/folders');
    return response.data;
  });
};

export const createFolder = async (folderData: CreateFolderRequest): Promise<DocumentFolder> => {
  return safeApiCall(async () => {
    const response = await apiClient.post('/api/folders', folderData);
    return response.data;
  });
};

export const updateFolder = async (
  id: string, 
  updates: { name?: string; color?: string }
): Promise<DocumentFolder> => {
  return safeApiCall(async () => {
    const response = await apiClient.put(`/api/folders/${id}`, updates);
    return response.data;
  });
};

export const deleteFolder = async (id: string): Promise<void> => {
  return safeApiCall(async () => {
    await apiClient.delete(`/api/folders/${id}`);
  });
};

// === FOLDER UTILITY FUNCTIONS ===

export const getFolderById = (folders: DocumentFolder[], id: string): DocumentFolder | undefined => {
  return folders.find(folder => folder.id === id);
};

export const getFolderName = (folders: DocumentFolder[], id: string): string => {
  const folder = getFolderById(folders, id);
  return folder?.name || 'Unknown Folder';
};

export const getSubfolders = (folders: DocumentFolder[], parentId: string): DocumentFolder[] => {
  return folders.filter(folder => folder.parent_id === parentId);
};

export const getRootFolders = (folders: DocumentFolder[]): DocumentFolder[] => {
  return folders.filter(folder => !folder.parent_id);
}; 
 