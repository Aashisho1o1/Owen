import axios from 'axios';

const API_URL = 'http://localhost:8000/api';

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

const api = {
  chat: async (request: ChatRequest): Promise<ChatResponse> => {
    const response = await axios.post<ChatResponse>(`${API_URL}/chat`, request);
    return response.data;
  },
  
  analyzeWriting: async (request: WritingSampleRequest): Promise<WritingSampleResponse> => {
    const response = await axios.post<WritingSampleResponse>(`${API_URL}/chat/analyze-writing`, request);
    return response.data;
  },
  
  submitFeedback: async (request: UserFeedbackRequest): Promise<{ status: string; message: string }> => {
    const response = await axios.post<{ status: string; message: string }>(`${API_URL}/chat/feedback`, request);
    return response.data;
  },
  
  completeOnboarding: async (request: OnboardingRequest): Promise<OnboardingResponse> => {
    const response = await axios.post<OnboardingResponse>(`${API_URL}/chat/onboarding`, request);
    return response.data;
  },
  
  getUserPreferences: async (): Promise<{ status: string; preferences?: UserPreferences; message?: string }> => {
    const response = await axios.get<{ status: string; preferences?: UserPreferences; message?: string }>(`${API_URL}/chat/preferences`);
    return response.data;
  },
  
  getStyleOptions: async (): Promise<{ english_variants: any[] }> => {
    const response = await axios.get<{ english_variants: any[] }>(`${API_URL}/chat/style-options`);
    return response.data;
  },
  
  createCheckpoint: async (request: CheckpointRequest): Promise<CheckpointResponse> => {
    const response = await axios.post<CheckpointResponse>(`${API_URL}/checkpoint`, request);
    return response.data;
  },
  
  healthCheck: async (): Promise<{ status: string }> => {
    const response = await axios.get<{ status: string }>(`${API_URL}/health`);
    return response.data;
  },

  generateMangaScript: async (request: MangaStoryRequest): Promise<MangaScriptResponseFE> => {
    const response = await axios.post<MangaScriptResponseFE>(`${API_URL}/manga/generate_script`, request);
    return response.data;
  },
};

export default api; 