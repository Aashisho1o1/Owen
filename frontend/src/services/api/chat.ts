/**
 * Chat API Service
 * Handles all chat-related API calls.
 */

import apiClient from './client';
import { ChatRequest, ChatResponse, EnhancedChatResponse, UserFeedbackRequest } from './types';
import { logger } from '../../utils/logger';

// === CHAT ENDPOINTS ===

export const sendChatMessage = async (request: ChatRequest): Promise<ChatResponse> => {
  const timeoutMs = request.voice_guard ? 150000 : 45000;

  if (request.voice_guard) {
    window.dispatchEvent(new CustomEvent('folderScopeProgress', {
      detail: { stage: 'starting', message: 'Running voice analysis...' }
    }));
  }

  try {
    const response = await apiClient.post('/api/chat/', request, {
      timeout: timeoutMs,
      headers: {
        'Content-Type': 'application/json',
        'X-Request-Type': request.voice_guard ? 'voice-guard' : 'standard',
      },
    });

    if (request.voice_guard) {
      window.dispatchEvent(new CustomEvent('folderScopeProgress', { detail: { stage: 'completed' } }));
    }
    return response.data;
  } catch (error: any) {
    logger.error('Chat request failed', {
      status: error.response?.status,
      message: error.message,
      timeout: error.code === 'ECONNABORTED',
    });

    if (request.voice_guard) {
      window.dispatchEvent(new CustomEvent('folderScopeProgress', {
        detail: {
          stage: 'error',
          message: `Request failed: ${error.response?.status || error.message}`
        }
      }));
    }

    throw error;
  }
};

export const generateSuggestions = async (request: ChatRequest): Promise<EnhancedChatResponse> => {
  const response = await apiClient.post('/api/chat/suggestions', request);
  return response.data;
};

export const submitUserFeedback = async (feedback: UserFeedbackRequest): Promise<{ success: boolean; message: string }> => {
  const response = await apiClient.post('/api/chat/feedback', feedback);
  return response.data;
};

export const getUserPreferences = async (): Promise<any> => {
  const response = await apiClient.get('/api/chat/preferences');
  return response.data;
};

export const acceptSuggestion = async (suggestionData: any): Promise<{ success: boolean; message: string }> => {
  const response = await apiClient.post('/api/chat/accept-suggestion', suggestionData);
  return response.data;
};

// === UTILITY FUNCTIONS ===

export interface BuildChatRequestOptions {
  message: string;
  editorText: string;
  authorPersona: string;
  helpFocus: string;
  chatHistory: any[];
  llmProvider: string;
  userPreferences?: any;
  feedbackOnPrevious?: string;
  highlightedText?: string;
  highlightId?: string;
  aiMode?: string;
  voiceGuard?: boolean;
}

export const buildChatRequest = (options: BuildChatRequestOptions): ChatRequest => {
  return {
    message: options.message,
    editor_text: options.editorText,
    author_persona: options.authorPersona,
    help_focus: options.helpFocus,
    chat_history: options.chatHistory,
    llm_provider: options.llmProvider,
    user_preferences: options.userPreferences || { user_corrections: [] },
    feedback_on_previous: options.feedbackOnPrevious || '',
    highlighted_text: options.highlightedText || '',
    highlight_id: options.highlightId || '',
    ai_mode: options.aiMode || 'talk',
    voice_guard: options.voiceGuard || false,
  };
};
