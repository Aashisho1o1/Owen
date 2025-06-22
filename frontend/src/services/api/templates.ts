/**
 * Templates API Service
 * Handles all template-related API calls.
 * Extracted from api.ts as part of God File refactoring.
 */

import { apiClient, safeApiCall } from './client';
import { DocumentTemplate } from './types';

// === TEMPLATE OPERATIONS ===

export const getTemplates = async (): Promise<DocumentTemplate[]> => {
  return safeApiCall(async () => {
    const response = await apiClient.get('/api/templates');
    return response.data;
  });
};

export const getTemplate = async (id: string): Promise<DocumentTemplate> => {
  return safeApiCall(async () => {
    const response = await apiClient.get(`/api/templates/${id}`);
    return response.data;
  });
};

// === TEMPLATE UTILITY FUNCTIONS ===

export const getTemplateById = (templates: DocumentTemplate[], id: string): DocumentTemplate | undefined => {
  return templates.find(template => template.id === id);
};

export const getTemplatesByCategory = (templates: DocumentTemplate[], category: string): DocumentTemplate[] => {
  return templates.filter(template => 
    template.document_type.toLowerCase() === category.toLowerCase()
  );
};

export const getSystemTemplates = (templates: DocumentTemplate[]): DocumentTemplate[] => {
  return templates.filter(template => template.is_system);
};

export const getUserTemplates = (templates: DocumentTemplate[]): DocumentTemplate[] => {
  return templates.filter(template => !template.is_system);
}; 
 