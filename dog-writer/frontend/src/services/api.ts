import axios from 'axios';

const API_URL = 'http://localhost:8000/api';

export interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
}

export interface ChatRequest {
  message: string;
  editor_text: string;
  author_persona: string;
  help_focus: string;
  chat_history: ChatMessage[];
  llm_provider: string;
}

export interface ChatResponse {
  dialogue_response: string;
  thinking_trail?: string | null;
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