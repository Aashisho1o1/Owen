import axios from 'axios';

// Normalise base URL: ensure it includes protocol so we never end up with
//   "backend-production-xxxx.up.railway.app" (missing scheme) which the browser
//   treats as a relative path.
const rawApiUrl = import.meta.env.VITE_API_URL || 'https://backend-production-1429.up.railway.app';
const API_URL = rawApiUrl.startsWith('http') ? rawApiUrl : `https://${rawApiUrl}`;

// Create axios instance with authentication support
const apiClient = axios.create({
  baseURL: API_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
    'X-Requested-With': 'XMLHttpRequest',
  },
});

// Add authentication token to requests
apiClient.interceptors.request.use(
  (config) => {
    // Add authentication token if available
    const token = localStorage.getItem('owen_access_token');
    const tokenType = localStorage.getItem('owen_token_type') || 'bearer';
    
    if (token && !config.headers['Authorization']) {
      config.headers['Authorization'] = `${tokenType} ${token}`;
    }
    
    console.log(`🔄 API Request: ${config.method?.toUpperCase()} ${config.url}`);
    console.log('Request data:', config.data);
    return config;
  },
  (error) => {
    console.error('❌ Request Error:', error);
    return Promise.reject(error);
  }
);

apiClient.interceptors.response.use(
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
  highlighted_text?: string;
  highlight_id?: string;
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
  document_type?: string;
  folder_id?: string;
  series_id?: string;
  chapter_number?: number;
}

export interface UpdateDocumentRequest {
  id: string;
  title?: string;
  content?: string;
  is_favorite?: boolean;
  tags?: string[];
}

export interface DocumentsResponse {
  documents: Document[];
  total: number;
}

export interface LoginRequest {
  username: string;
  password: string;
}

export interface RegisterRequest {
  username: string;
  name: string;
  email: string;
  password: string;
}

export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
}

export interface UserProfile {
  id: number;
  username: string;
  name: string;
  email: string;
}

const api = {
  chat: async (request: ChatRequest): Promise<ChatResponse> => {
    const response = await apiClient.post<ChatResponse>('/api/chat/message', request);
    return response.data;
  },
  
  analyzeWriting: async (request: WritingSampleRequest): Promise<WritingSampleResponse> => {
    const response = await apiClient.post<WritingSampleResponse>('/api/chat/analyze-writing', request);
    return response.data;
  },
  
  submitFeedback: async (request: UserFeedbackRequest): Promise<{ status: string; message: string }> => {
    const response = await apiClient.post<{ status: string; message: string }>('/api/chat/feedback', request);
    return response.data;
  },
  
  completeOnboarding: async (request: OnboardingRequest): Promise<OnboardingResponse> => {
    const response = await apiClient.post<OnboardingResponse>('/api/chat/onboarding', request);
    return response.data;
  },
  
  getUserPreferences: async (): Promise<{ status: string; preferences?: UserPreferences; message?: string }> => {
    const response = await apiClient.get<{ status: string; preferences?: UserPreferences; message?: string }>('/api/chat/preferences');
    return response.data;
  },
  
  getStyleOptions: async (): Promise<{ english_variants: any[] }> => {
    const response = await apiClient.get<{ english_variants: any[] }>('/api/chat/style-options');
    return response.data;
  },
  
  createCheckpoint: async (request: CheckpointRequest): Promise<CheckpointResponse> => {
    const response = await apiClient.post<CheckpointResponse>('/api/checkpoint', request);
    return response.data;
  },
  
  healthCheck: async (): Promise<{ status: string }> => {
    const response = await apiClient.get<{ status: string }>('/api/health');
    return response.data;
  },

  generateMangaScript: async (request: MangaStoryRequest): Promise<MangaScriptResponseFE> => {
    const response = await apiClient.post<MangaScriptResponseFE>('/api/manga/generate_script', request);
    return response.data;
  },

  // Document Management APIs
  getDocuments: async (): Promise<DocumentsResponse> => {
    const response = await apiClient.get<DocumentsResponse>('/api/documents');
    return response.data;
  },

  getDocument: async (id: string): Promise<Document> => {
    const response = await apiClient.get<Document>(`/api/documents/${id}`);
    return response.data;
  },

  createDocument: async (request: CreateDocumentRequest): Promise<Document> => {
    const response = await apiClient.post<Document>('/api/documents', request);
    return response.data;
  },

  updateDocument: async (request: UpdateDocumentRequest): Promise<Document> => {
    const { id, ...updateData } = request;
    const response = await apiClient.put<Document>(`/api/documents/${id}`, updateData);
    return response.data;
  },

  deleteDocument: async (id: string): Promise<{ success: boolean; message: string }> => {
    const response = await apiClient.delete<{ success: boolean; message: string }>(`/api/documents/${id}`);
    return response.data;
  },

  // VERSION MANAGEMENT
  getDocumentVersions: async (documentId: string): Promise<DocumentVersion[]> => {
    const response = await apiClient.get<DocumentVersion[]>(`/api/documents/${documentId}/versions`);
    return response.data;
  },

  restoreDocumentVersion: async (documentId: string, versionId: string): Promise<Document> => {
    const response = await apiClient.post<Document>(`/api/documents/${documentId}/versions/${versionId}/restore`);
    return response.data;
  },

  compareVersions: async (documentId: string, version1: string, version2: string): Promise<any> => {
    const response = await apiClient.get(`/api/documents/${documentId}/versions/compare?v1=${version1}&v2=${version2}`);
    return response.data;
  },

  // FOLDER MANAGEMENT
  getFolders: async (): Promise<DocumentFolder[]> => {
    const response = await apiClient.get<DocumentFolder[]>('/api/folders');
    return response.data;
  },

  createFolder: async (name: string, parentId?: string, color?: string): Promise<DocumentFolder> => {
    const response = await apiClient.post<DocumentFolder>('/api/folders', {
      name,
      parent_id: parentId,
      color
    });
    return response.data;
  },

  updateFolder: async (folderId: string, updates: Partial<DocumentFolder>): Promise<DocumentFolder> => {
    const response = await apiClient.put<DocumentFolder>(`/api/folders/${folderId}`, updates);
    return response.data;
  },

  deleteFolder: async (folderId: string, moveDocumentsTo?: string): Promise<{ success: boolean }> => {
    const response = await apiClient.delete(`/api/folders/${folderId}`, {
      data: { move_documents_to: moveDocumentsTo }
    });
    return response.data;
  },

  // SERIES MANAGEMENT
  getSeries: async (): Promise<DocumentSeries[]> => {
    const response = await apiClient.get<DocumentSeries[]>('/api/series');
    return response.data;
  },

  createSeries: async (name: string, description?: string): Promise<DocumentSeries> => {
    const response = await apiClient.post<DocumentSeries>('/api/series', {
      name,
      description
    });
    return response.data;
  },

  updateSeries: async (seriesId: string, updates: Partial<DocumentSeries>): Promise<DocumentSeries> => {
    const response = await apiClient.put<DocumentSeries>(`/api/series/${seriesId}`, updates);
    return response.data;
  },

  deleteSeries: async (seriesId: string): Promise<{ success: boolean }> => {
    const response = await apiClient.delete(`/api/series/${seriesId}`);
    return response.data;
  },

  // TEMPLATES
  getTemplates: async (): Promise<DocumentTemplate[]> => {
    const response = await apiClient.get<DocumentTemplate[]>('/api/templates');
    return response.data;
  },

  createDocumentFromTemplate: async (templateId: string, title: string, folderId?: string): Promise<Document> => {
    const response = await apiClient.post<Document>('/api/documents/from-template', {
      template_id: templateId,
      title,
      folder_id: folderId
    });
    return response.data;
  },

  // ADVANCED SEARCH
  searchDocuments: async (searchRequest: SearchRequest): Promise<SearchResult[]> => {
    const response = await apiClient.post<SearchResult[]>('/api/search', searchRequest);
    return response.data;
  },

  // EXPORT FUNCTIONALITY
  exportDocument: async (exportRequest: ExportRequest): Promise<Blob> => {
    const response = await apiClient.post('/api/export', exportRequest, {
      responseType: 'blob'
    });
    return response.data;
  },

  // WRITING ANALYTICS
  getWritingGoals: async (): Promise<WritingGoal[]> => {
    const response = await apiClient.get<WritingGoal[]>('/api/goals');
    return response.data;
  },

  createWritingGoal: async (goal: Omit<WritingGoal, 'id' | 'user_id' | 'current_words'>): Promise<WritingGoal> => {
    const response = await apiClient.post<WritingGoal>('/api/goals', goal);
    return response.data;
  },

  getWritingSessions: async (documentId?: string, dateRange?: { start: string; end: string }): Promise<WritingSession[]> => {
    const params = new URLSearchParams();
    if (documentId) params.append('document_id', documentId);
    if (dateRange) {
      params.append('start_date', dateRange.start);
      params.append('end_date', dateRange.end);
    }
    
    const response = await apiClient.get<WritingSession[]>(`/api/sessions?${params}`);
    return response.data;
  },

  getWritingStats: async (period: 'week' | 'month' | 'year'): Promise<any> => {
    const response = await apiClient.get(`/api/stats/writing?period=${period}`);
    return response.data;
  },

  // BACKUP & SYNC
  createBackup: async (): Promise<{ backup_id: string; download_url: string }> => {
    const response = await apiClient.post('/api/backup');
    return response.data;
  },

  restoreFromBackup: async (backupId: string): Promise<{ success: boolean; message: string }> => {
    const response = await apiClient.post(`/api/backup/${backupId}/restore`);
    return response.data;
  },

  // COLLABORATION
  shareDocument: async (documentId: string, email: string, permission: 'view' | 'comment' | 'edit'): Promise<any> => {
    const response = await apiClient.post(`/api/documents/${documentId}/share`, {
      email,
      permission
    });
    return response.data;
  },

  getDocumentShares: async (documentId: string): Promise<any[]> => {
    const response = await apiClient.get(`/api/documents/${documentId}/shares`);
    return response.data;
  },

  // ENHANCED DOCUMENT OPERATIONS
  duplicateDocument: async (documentId: string, newTitle?: string): Promise<Document> => {
    const response = await apiClient.post<Document>(`/api/documents/${documentId}/duplicate`, {
      new_title: newTitle
    });
    return response.data;
  },

  moveDocument: async (documentId: string, folderId?: string, seriesId?: string): Promise<Document> => {
    const response = await apiClient.put<Document>(`/api/documents/${documentId}/move`, {
      folder_id: folderId,
      series_id: seriesId
    });
    return response.data;
  },

  addDocumentTags: async (documentId: string, tags: string[]): Promise<Document> => {
    const response = await apiClient.post<Document>(`/api/documents/${documentId}/tags`, { tags });
    return response.data;
  },

  getDocumentAnalytics: async (documentId: string): Promise<any> => {
    const response = await apiClient.get(`/api/documents/${documentId}/analytics`);
    return response.data;
  },

  // Auth APIs
  login: async (request: LoginRequest): Promise<TokenResponse> => {
    const response = await apiClient.post<TokenResponse>('/api/auth/login', request);
    return response.data;
  },

  register: async (request: RegisterRequest): Promise<TokenResponse> => {
    const response = await apiClient.post<TokenResponse>('/api/auth/register', request);
    return response.data;
  },

  getUserProfile: async (): Promise<UserProfile> => {
    const response = await apiClient.get<UserProfile>('/api/auth/profile');
    return response.data;
  },
};

export default api; 