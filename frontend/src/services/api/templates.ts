/**
 * Template API Service
 * Handles all template-related API calls.
 */

import apiClient from './client';
import { DocumentTemplate } from './types';

// === TEMPLATE OPERATIONS ===

export const getTemplates = async (): Promise<DocumentTemplate[]> => {
  const response = await apiClient.get('/api/fiction-templates');
  return response.data;
};

export const getTemplate = async (id: string): Promise<DocumentTemplate> => {
  const response = await apiClient.get(`/api/fiction-templates/${id}`);
  return response.data;
};

// === TEMPLATE UTILITY FUNCTIONS ===

export const getTemplateById = (templates: DocumentTemplate[], id: string): DocumentTemplate | undefined => {
  return templates.find(template => template.id === id);
};

export const getTemplatesByCategory = (templates: DocumentTemplate[], category: string): DocumentTemplate[] => {
  return templates.filter(template => 
    template.category?.toLowerCase() === category.toLowerCase()
  );
};

export const getSystemTemplates = (templates: DocumentTemplate[]): DocumentTemplate[] => {
  return templates.filter(template => template.is_system_template);
};

export const getUserTemplates = (templates: DocumentTemplate[]): DocumentTemplate[] => {
  return templates.filter(template => !template.is_system_template);
}; 
 