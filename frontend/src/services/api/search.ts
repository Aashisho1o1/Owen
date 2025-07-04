/**
 * Search API Service
 * Handles all search-related API calls.
 * Extracted from api.ts as part of God File refactoring.
 */

import apiClient from './client';
import { SearchRequest, SearchResult, Document } from './types';

// === SEARCH ENDPOINTS ===

export const searchDocuments = async (searchData: SearchRequest): Promise<SearchResult[]> => {
  const response = await apiClient.post('/api/search', searchData);
  return response.data;
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
  const { 
    searchInContent = true, 
    searchInTags = true, 
    caseSensitive = false 
  } = options || {};
  
  const searchTerm = caseSensitive ? query : query.toLowerCase();
  
  return documents.filter(doc => {
    const title = caseSensitive ? doc.title : doc.title.toLowerCase();
    const content = caseSensitive ? (doc.content || '') : (doc.content || '').toLowerCase();
    const tags = doc.tags?.map(tag => caseSensitive ? tag : tag.toLowerCase()) || [];
    
    // Search in title
    if (title.includes(searchTerm)) return true;
    
    // Search in content if enabled
    if (searchInContent && content.includes(searchTerm)) return true;
    
    // Search in tags if enabled
    if (searchInTags && tags.some(tag => tag.includes(searchTerm))) return true;
    
    return false;
  });
};

// === SEARCH REQUEST BUILDERS ===

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
    filters: {
      document_ids: options?.documentIds,
      folder_ids: options?.folderIds,
      tags: options?.tags,
      document_types: options?.documentTypes,
      content_only: options?.contentOnly || false
    }
  };
};

// === SEARCH RESULT UTILITIES ===

export const highlightSearchMatches = (text: string, query: string): string => {
  if (!query.trim()) return text;
  
  const regex = new RegExp(`(${query.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')})`, 'gi');
  return text.replace(regex, '<mark>$1</mark>');
}; 
 