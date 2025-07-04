/**
 * Chat API Service
 * Handles all chat-related API calls.
 * Extracted from api.ts as part of God File refactoring.
 */

import apiClient from './client';
import { ChatRequest, ChatResponse, EnhancedChatResponse, UserFeedbackRequest } from './types';

// === CHAT ENDPOINTS ===

export const sendChatMessage = async (request: ChatRequest): Promise<ChatResponse> => {
  const response = await apiClient.post('/api/chat/', request);
  return response.data;
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

export const buildChatRequest = (
  message: string,
  editorText: string,
  authorPersona: string,
  helpFocus: string,
  chatHistory: any[],
  llmProvider: string,
  userPreferences?: any,
  feedbackOnPrevious?: string,
  highlightedText?: string,
  highlightId?: string,
  aiMode: string = 'talk'
): ChatRequest => {
  return {
    message,
    editor_text: editorText,
    author_persona: authorPersona,
    help_focus: helpFocus,
    chat_history: chatHistory,
    llm_provider: llmProvider,
    user_preferences: userPreferences || { user_corrections: [] },
    feedback_on_previous: feedbackOnPrevious || '',
    highlighted_text: highlightedText || '',
    highlight_id: highlightId || '',
    ai_mode: aiMode
  };
}; 