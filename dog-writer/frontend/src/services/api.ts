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
}

export interface ChatResponse {
  dialogue_response: string;
  fill_in_the_blanks_suggestion: string | null;
  reasoning: string;
}

export interface CheckpointRequest {
  editor_text: string;
  chat_history: ChatMessage[];
}

export interface CheckpointResponse {
  status: string;
  message: string;
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
  }
};

export default api; 