import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'https://backend-production-ea53.up.railway.app';

// Add axios interceptors for better error handling and logging
axios.interceptors.request.use(
  (config) => {
    console.log(`🔄 API Request: ${config.method?.toUpperCase()} ${config.url}`);
    console.log('Request data:', config.data);
    return config;
  },
  (error) => {
    console.error('❌ Request Error:', error);
    return Promise.reject(error);
  }
);

axios.interceptors.response.use(
  (response) => {
    console.log(`✅ API Response: ${response.config.method?.toUpperCase()} ${response.config.url} - ${response.status}`);
    return response;
  },
  (error) => {
    console.error('❌ Response Error:', {
      url: error.config?.url,
      method: error.config?.method,
      status: error.response?.status,
      statusText: error.response?.statusText,
      data: error.response?.data,
      message: error.message
    });
    
    // Enhanced error message for user
    if (error.code === 'ECONNREFUSED' || error.message.includes('Network Error')) {
      error.userMessage = 'Unable to connect to the server. Please check if the backend is running.';
    } else if (error.response?.status === 500) {
      error.userMessage = 'Server error occurred. Please try again later.';
    } else if (error.response?.status === 404) {
      error.userMessage = 'API endpoint not found. Please check your configuration.';
    } else {
      error.userMessage = error.response?.data?.detail || error.response?.data?.error || error.message;
    }
    
    return Promise.reject(error);
  }
);

export interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
}

export interface UserPreferences {
  english_variant: string;
  writing_style_profile?: any;
  onboarding_completed: boolean;
  user_corrections: string[];
  writing_type?: string;
  feedback_style?: string;
  primary_goal?: string;
}

export interface ChatRequest {
  message: string;
  editor_text: string;
  author_persona: string;
  help_focus: string;
  chat_history: ChatMessage[];
  llm_provider: string;
  user_preferences?: UserPreferences;
  feedback_on_previous?: string;
  english_variant?: string;
}

export interface ChatResponse {
  dialogue_response: string;
  thinking_trail?: string | null;
}

export interface WritingSampleRequest {
  writing_sample: string;
  user_id?: string;
}

export interface WritingSampleResponse {
  style_profile: any;
  success: boolean;
  error?: string;
}

export interface UserFeedbackRequest {
  original_message: string;
  ai_response: string;
  user_feedback: string;
  correction_type: string;
}

export interface OnboardingRequest {
  writing_type: string;
  feedback_style: string;
  primary_goal: string;
  english_variant: string;
}

export interface OnboardingResponse {
  success: boolean;
  user_preferences: UserPreferences;
  message: string;
}

export interface CheckpointRequest {
  editor_text: string;
  chat_history: ChatMessage[];
}

export interface CheckpointResponse {
  status: string;
  message: string;
}

export interface MangaStoryRequest {
  story_text: string;
  author_persona: string;
}

export interface MangaPanelDialogueFE {
  character: string;
  speech: string;
}

export interface MangaPanelFE {
  panel_number: number;
  description: string;
  dialogue: MangaPanelDialogueFE[];
  image_url?: string | null;
}

export interface MangaPageFE {
  title: string;
  page_number: number;
  character_designs: Record<string, string>;
  panels: MangaPanelFE[];
}

export interface MangaScriptResponseFE {
  manga_page?: MangaPageFE | null;
  error?: string | null;
}

// Document Management Interfaces
export interface Document {
  id: string;
  title: string;
  content: string;
  created_at: string;
  updated_at: string;
  user_id: string;
  is_favorite?: boolean;
  word_count?: number;
  folder_id?: string;
  tags?: string[];
  document_type?: 'novel' | 'chapter' | 'character_sheet' | 'outline' | 'notes';
  series_id?: string;
  chapter_number?: number;
  status?: 'draft' | 'revision' | 'final' | 'published';
}

export interface DocumentVersion {
  id: string;
  document_id: string;
  version_number: number;
  content: string;
  title: string;
  created_at: string;
  word_count: number;
  change_summary: string;
  is_auto_save: boolean;
}

export interface DocumentFolder {
  id: string;
  name: string;
  parent_id?: string;
  user_id: string;
  created_at: string;
  color?: string;
  icon?: string;
  document_count?: number;
}

export interface DocumentSeries {
  id: string;
  name: string;
  description?: string;
  user_id: string;
  created_at: string;
  document_count?: number;
  total_word_count?: number;
  status?: 'planning' | 'writing' | 'editing' | 'complete';
}

export interface DocumentTemplate {
  id: string;
  name: string;
  content: string;
  document_type: string;
  is_system: boolean;
  user_id?: string;
  preview_text: string;
}

export interface WritingGoal {
  id: string;
  user_id: string;
  goal_type: 'daily' | 'weekly' | 'monthly' | 'project';
  target_words: number;
  current_words: number;
  start_date: string;
  end_date?: string;
  document_id?: string;
  series_id?: string;
}

export interface WritingSession {
  id: string;
  user_id: string;
  document_id: string;
  start_time: string;
  end_time?: string;
  words_written: number;
  time_spent_minutes: number;
  session_type: 'writing' | 'editing' | 'planning';
}

export interface ExportRequest {
  document_id: string;
  format: 'pdf' | 'docx' | 'epub' | 'txt' | 'html';
  include_metadata?: boolean;
  custom_styling?: any;
}

export interface SearchRequest {
  query: string;
  document_ids?: string[];
  folder_ids?: string[];
  series_ids?: string[];
  tags?: string[];
  document_types?: string[];
  date_range?: {
    start: string;
    end: string;
  };
  content_only?: boolean;
}

export interface SearchResult {
  document_id: string;
  document_title: string;
  matches: {
    content: string;
    context: string;
    position: number;
  }[];
  relevance_score: number;
}

export interface CreateDocumentRequest {
  title: string;
  content?: string;
}

export interface UpdateDocumentRequest {
  id: string;
  title?: string;
  content?: string;
  is_favorite?: boolean;
}

export interface DocumentsResponse {
  documents: Document[];
  total: number;
}

const api = {
  chat: async (request: ChatRequest): Promise<ChatResponse> => {
    const response = await axios.post<ChatResponse>(`${API_URL}/api/chat/message`, request);
    return response.data;
  },
  
  analyzeWriting: async (request: WritingSampleRequest): Promise<WritingSampleResponse> => {
    const response = await axios.post<WritingSampleResponse>(`${API_URL}/api/chat/analyze-writing`, request);
    return response.data;
  },
  
  submitFeedback: async (request: UserFeedbackRequest): Promise<{ status: string; message: string }> => {
    const response = await axios.post<{ status: string; message: string }>(`${API_URL}/api/chat/feedback`, request);
    return response.data;
  },
  
  completeOnboarding: async (request: OnboardingRequest): Promise<OnboardingResponse> => {
    const response = await axios.post<OnboardingResponse>(`${API_URL}/api/chat/onboarding`, request);
    return response.data;
  },
  
  getUserPreferences: async (): Promise<{ status: string; preferences?: UserPreferences; message?: string }> => {
    const response = await axios.get<{ status: string; preferences?: UserPreferences; message?: string }>(`${API_URL}/api/chat/preferences`);
    return response.data;
  },
  
  getStyleOptions: async (): Promise<{ english_variants: any[] }> => {
    const response = await axios.get<{ english_variants: any[] }>(`${API_URL}/api/chat/style-options`);
    return response.data;
  },
  
  createCheckpoint: async (request: CheckpointRequest): Promise<CheckpointResponse> => {
    const response = await axios.post<CheckpointResponse>(`${API_URL}/api/checkpoint`, request);
    return response.data;
  },
  
  healthCheck: async (): Promise<{ status: string }> => {
    const response = await axios.get<{ status: string }>(`${API_URL}/api/health`);
    return response.data;
  },

  generateMangaScript: async (request: MangaStoryRequest): Promise<MangaScriptResponseFE> => {
    const response = await axios.post<MangaScriptResponseFE>(`${API_URL}/api/manga/generate_script`, request);
    return response.data;
  },

  // Document Management APIs
  getDocuments: async (): Promise<DocumentsResponse> => {
    const response = await axios.get<DocumentsResponse>(`${API_URL}/api/documents`);
    return response.data;
  },

  getDocument: async (id: string): Promise<Document> => {
    const response = await axios.get<Document>(`${API_URL}/api/documents/${id}`);
    return response.data;
  },

  createDocument: async (request: CreateDocumentRequest): Promise<Document> => {
    const response = await axios.post<Document>(`${API_URL}/api/documents`, request);
    return response.data;
  },

  updateDocument: async (request: UpdateDocumentRequest): Promise<Document> => {
    const { id, ...updateData } = request;
    const response = await axios.put<Document>(`${API_URL}/api/documents/${id}`, updateData);
    return response.data;
  },

  deleteDocument: async (id: string): Promise<{ success: boolean; message: string }> => {
    const response = await axios.delete<{ success: boolean; message: string }>(`${API_URL}/api/documents/${id}`);
    return response.data;
  },

  // VERSION MANAGEMENT
  getDocumentVersions: async (documentId: string): Promise<DocumentVersion[]> => {
    const response = await axios.get<DocumentVersion[]>(`${API_URL}/api/documents/${documentId}/versions`);
    return response.data;
  },

  restoreDocumentVersion: async (documentId: string, versionId: string): Promise<Document> => {
    const response = await axios.post<Document>(`${API_URL}/api/documents/${documentId}/versions/${versionId}/restore`);
    return response.data;
  },

  compareVersions: async (documentId: string, version1: string, version2: string): Promise<any> => {
    const response = await axios.get(`${API_URL}/api/documents/${documentId}/versions/compare?v1=${version1}&v2=${version2}`);
    return response.data;
  },

  // FOLDER MANAGEMENT
  getFolders: async (): Promise<DocumentFolder[]> => {
    const response = await axios.get<DocumentFolder[]>(`${API_URL}/api/folders`);
    return response.data;
  },

  createFolder: async (name: string, parentId?: string, color?: string): Promise<DocumentFolder> => {
    const response = await axios.post<DocumentFolder>(`${API_URL}/api/folders`, {
      name,
      parent_id: parentId,
      color
    });
    return response.data;
  },

  updateFolder: async (folderId: string, updates: Partial<DocumentFolder>): Promise<DocumentFolder> => {
    const response = await axios.put<DocumentFolder>(`${API_URL}/api/folders/${folderId}`, updates);
    return response.data;
  },

  deleteFolder: async (folderId: string, moveDocumentsTo?: string): Promise<{ success: boolean }> => {
    const response = await axios.delete(`${API_URL}/api/folders/${folderId}`, {
      data: { move_documents_to: moveDocumentsTo }
    });
    return response.data;
  },

  // SERIES MANAGEMENT
  getSeries: async (): Promise<DocumentSeries[]> => {
    const response = await axios.get<DocumentSeries[]>(`${API_URL}/api/series`);
    return response.data;
  },

  createSeries: async (name: string, description?: string): Promise<DocumentSeries> => {
    const response = await axios.post<DocumentSeries>(`${API_URL}/api/series`, {
      name,
      description
    });
    return response.data;
  },

  updateSeries: async (seriesId: string, updates: Partial<DocumentSeries>): Promise<DocumentSeries> => {
    const response = await axios.put<DocumentSeries>(`${API_URL}/api/series/${seriesId}`, updates);
    return response.data;
  },

  deleteSeries: async (seriesId: string): Promise<{ success: boolean }> => {
    const response = await axios.delete(`${API_URL}/api/series/${seriesId}`);
    return response.data;
  },

  // TEMPLATES
  getTemplates: async (): Promise<DocumentTemplate[]> => {
    const response = await axios.get<DocumentTemplate[]>(`${API_URL}/api/templates`);
    return response.data;
  },

  createDocumentFromTemplate: async (templateId: string, title: string, folderId?: string): Promise<Document> => {
    const response = await axios.post<Document>(`${API_URL}/api/documents/from-template`, {
      template_id: templateId,
      title,
      folder_id: folderId
    });
    return response.data;
  },

  // ADVANCED SEARCH
  searchDocuments: async (searchRequest: SearchRequest): Promise<SearchResult[]> => {
    const response = await axios.post<SearchResult[]>(`${API_URL}/api/search`, searchRequest);
    return response.data;
  },

  // EXPORT FUNCTIONALITY
  exportDocument: async (exportRequest: ExportRequest): Promise<Blob> => {
    const response = await axios.post(`${API_URL}/api/export`, exportRequest, {
      responseType: 'blob'
    });
    return response.data;
  },

  // WRITING ANALYTICS
  getWritingGoals: async (): Promise<WritingGoal[]> => {
    const response = await axios.get<WritingGoal[]>(`${API_URL}/api/goals`);
    return response.data;
  },

  createWritingGoal: async (goal: Omit<WritingGoal, 'id' | 'user_id' | 'current_words'>): Promise<WritingGoal> => {
    const response = await axios.post<WritingGoal>(`${API_URL}/api/goals`, goal);
    return response.data;
  },

  getWritingSessions: async (documentId?: string, dateRange?: { start: string; end: string }): Promise<WritingSession[]> => {
    const params = new URLSearchParams();
    if (documentId) params.append('document_id', documentId);
    if (dateRange) {
      params.append('start_date', dateRange.start);
      params.append('end_date', dateRange.end);
    }
    
    const response = await axios.get<WritingSession[]>(`${API_URL}/api/sessions?${params}`);
    return response.data;
  },

  getWritingStats: async (period: 'week' | 'month' | 'year'): Promise<any> => {
    const response = await axios.get(`${API_URL}/api/stats/writing?period=${period}`);
    return response.data;
  },

  // BACKUP & SYNC
  createBackup: async (): Promise<{ backup_id: string; download_url: string }> => {
    const response = await axios.post(`${API_URL}/api/backup`);
    return response.data;
  },

  restoreFromBackup: async (backupId: string): Promise<{ success: boolean; message: string }> => {
    const response = await axios.post(`${API_URL}/api/backup/${backupId}/restore`);
    return response.data;
  },

  // COLLABORATION
  shareDocument: async (documentId: string, email: string, permission: 'view' | 'comment' | 'edit'): Promise<any> => {
    const response = await axios.post(`${API_URL}/api/documents/${documentId}/share`, {
      email,
      permission
    });
    return response.data;
  },

  getDocumentShares: async (documentId: string): Promise<any[]> => {
    const response = await axios.get(`${API_URL}/api/documents/${documentId}/shares`);
    return response.data;
  },

  // ENHANCED DOCUMENT OPERATIONS
  duplicateDocument: async (documentId: string, newTitle?: string): Promise<Document> => {
    const response = await axios.post<Document>(`${API_URL}/api/documents/${documentId}/duplicate`, {
      new_title: newTitle
    });
    return response.data;
  },

  moveDocument: async (documentId: string, folderId?: string, seriesId?: string): Promise<Document> => {
    const response = await axios.put<Document>(`${API_URL}/api/documents/${documentId}/move`, {
      folder_id: folderId,
      series_id: seriesId
    });
    return response.data;
  },

  addDocumentTags: async (documentId: string, tags: string[]): Promise<Document> => {
    const response = await axios.post<Document>(`${API_URL}/api/documents/${documentId}/tags`, { tags });
    return response.data;
  },

  getDocumentAnalytics: async (documentId: string): Promise<any> => {
    const response = await axios.get(`${API_URL}/api/documents/${documentId}/analytics`);
    return response.data;
  },
};

export default api; 