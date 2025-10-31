/**
 * API Service - Minimal backend integration
 * Connects to our new minimal backend (main-new-Google branch)
 */

import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add auth token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('auth_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// === AUTH ===

export interface UserRegister {
  email: string;
  password: string;
}

export interface UserLogin {
  email: string;
  password: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
  user_id: number;
}

export const authAPI = {
  register: async (data: UserRegister): Promise<TokenResponse> => {
    const response = await api.post('/api/auth/register', data);
    return response.data;
  },

  login: async (data: UserLogin): Promise<TokenResponse> => {
    const response = await api.post('/api/auth/login', data);
    return response.data;
  },
};

// === VOICE ANALYSIS ===

export interface VoiceAnalysisRequest {
  text: string;
}

export interface VoiceAnalysisResult {
  character_name: string;
  is_consistent: boolean;
  confidence_score: number;
  voice_traits: {
    formality?: string;
    vocabulary?: string;
    tone?: string;
    complexity?: string;
  };
  issues: string[];
  suggestions: string[];
  flagged_text?: string;
}

export interface VoiceAnalysisResponse {
  results: VoiceAnalysisResult[];
  characters_analyzed: number;
  dialogue_segments_found: number;
  processing_time_ms: number;
}

export interface CharacterProfile {
  id: number;
  character_name: string;
  dialogue_samples: string[];
  voice_traits: Record<string, any>;
  sample_count: number;
  last_updated: string;
}

export interface CharacterProfilesResponse {
  profiles: CharacterProfile[];
}

export const voiceAPI = {
  analyze: async (data: VoiceAnalysisRequest): Promise<VoiceAnalysisResponse> => {
    const response = await api.post('/api/voice/analyze', data);
    return response.data;
  },

  getProfiles: async (): Promise<CharacterProfilesResponse> => {
    const response = await api.get('/api/voice/profiles');
    return response.data;
  },

  deleteProfile: async (characterName: string): Promise<void> => {
    await api.delete(`/api/voice/profiles/${encodeURIComponent(characterName)}`);
  },
};

// === HEALTH CHECK ===

export const healthAPI = {
  check: async () => {
    const response = await api.get('/health');
    return response.data;
  },
};

export default api;
