/**
 * Search API Service
 * Handles all search-related API calls.
 * Extracted from api.ts as part of God File refactoring.
 */

import { apiClient, safeApiCall } from './client';
import { SearchRequest, SearchResult, Document } from './types';

// === SEARCH ENDPOINTS ===

export const searchDocuments = async (searchData: SearchRequest): Promise<SearchResult[]> => {
  return safeApiCall(async () => {
    const response = await apiClient.post('/api/documents/search', searchData);
    return response.data.results || [];
  });
};

// === LOCAL SEARCH UTILITIES ===

export const searchDocumentsLocally = (
  documents: Document[], 
  query: string,
  options?: {
    searchInContent?: boolean;
    searchInTags?: boolean;
    caseSensitive?: boolean;
  }
): Document[] => {
  if (!query.trim()) return documents;
  
  const searchTerm = options?.caseSensitive ? query : query.toLowerCase();
  
  return documents.filter(doc => {
    // Search in title (always)
    const titleMatch = options?.caseSensitive 
      ? doc.title.includes(searchTerm)
      : doc.title.toLowerCase().includes(searchTerm);
    
    if (titleMatch) return true;
    
    // Search in content if enabled
    if (options?.searchInContent && doc.content) {
      const contentMatch = options?.caseSensitive
        ? doc.content.includes(searchTerm)
        : doc.content.toLowerCase().includes(searchTerm);
      
      if (contentMatch) return true;
    }
    
    // Search in tags if enabled
    if (options?.searchInTags && doc.tags && doc.tags.length > 0) {
      const tagsMatch = doc.tags.some(tag => 
        options?.caseSensitive 
          ? tag.includes(searchTerm)
          : tag.toLowerCase().includes(searchTerm)
      );
      
      if (tagsMatch) return true;
    }
    
    return false;
  });
};

export const buildSearchRequest = (
  query: string,
  options?: {
    documentIds?: string[];
    folderIds?: string[];
    tags?: string[];
    documentTypes?: string[];
    contentOnly?: boolean;
  }
): SearchRequest => {
  return {
    query,
    document_ids: options?.documentIds,
    folder_ids: options?.folderIds,
    tags: options?.tags,
    document_types: options?.documentTypes,
    content_only: options?.contentOnly || false
  };
};

export const highlightSearchMatches = (text: string, query: string): string => {
  if (!query.trim()) return text;
  
  const regex = new RegExp(`(${query.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')})`, 'gi');
  return text.replace(regex, '<mark>$1</mark>');
}; 
 