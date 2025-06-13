import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

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
};

export default api; 