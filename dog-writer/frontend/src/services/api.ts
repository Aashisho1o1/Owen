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

export interface TranscriptionResponse {
  transcription: string;
  error?: string;
}

export interface OrganizedIdeaResponse {
  original_text?: string;
  summary?: string;
  category?: string;
  error?: string;
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

  async transcribeAudio(audioBlob: Blob): Promise<TranscriptionResponse> {
    const formData = new FormData();
    formData.append('audio_file', audioBlob, 'dictation.webm'); // Ensure filename and type are appropriate
    try {
      const response = await axios.post<TranscriptionResponse>(`${API_URL}/voice/transcribe`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      return response.data;
    } catch (error: any) {
      console.error("Error transcribing audio:", error.response?.data || error.message);
      return { transcription: '', error: error.response?.data?.detail || error.message || 'Transcription failed' };
    }
  },

  async organizeIdea(text: string): Promise<OrganizedIdeaResponse> {
    try {
      const response = await axios.post<OrganizedIdeaResponse>(`${API_URL}/voice/organize_idea`, { text });
      return response.data;
    } catch (error: any) {
      console.error("Error organizing idea:", error.response?.data || error.message);
      return { error: error.response?.data?.detail || error.message || 'Organization failed' };
    }
  },

  async synthesizeSpeech(text: string): Promise<Blob | null> {
    try {
      const response = await axios.post<Blob>(`${API_URL}/voice/synthesize`, 
        { text },
        { responseType: 'blob' } // Important: tells Axios to expect binary data (audio)
      );
      return response.data;
    } catch (error: any) {
      console.error("Error synthesizing speech:", error.response?.data || error.message);
      // If error.response.data is a Blob, it might contain an error message if the server sends JSON error as blob
      // This part might need refinement based on how backend errors are sent for blob responses.
      return null;
    }
  },
};

export default api; 