/**
 * Chat API Service
 * Handles all AI chat and writing assistance API calls.
 * Extracted from api.ts as part of God File refactoring.
 */

import { apiClient, safeApiCall } from './client';
import { 
  ChatRequest, 
  ChatResponse, 
  UserFeedbackRequest,
  UserPreferences,
  WritingSampleRequest,
  WritingSampleResponse,
  OnboardingRequest,
  OnboardingResponse,
  CheckpointRequest,
  CheckpointResponse
} from './types';

// === CHAT ENDPOINTS ===

export const sendChatMessage = async (chatData: ChatRequest): Promise<ChatResponse> => {
  return safeApiCall(async () => {
    const response = await apiClient.post('/api/chat', chatData);
    return response.data;
  });
};

export const submitUserFeedback = async (feedbackData: UserFeedbackRequest): Promise<{ status: string; message: string }> => {
  return safeApiCall(async () => {
    const response = await apiClient.post('/api/chat/feedback', feedbackData);
    return response.data;
  });
};

export const getUserPreferences = async (): Promise<{ status: string; preferences: UserPreferences }> => {
  return safeApiCall(async () => {
    const response = await apiClient.get('/api/chat/preferences');
    return response.data;
  });
};

// === WRITING ASSISTANCE ENDPOINTS ===

export const analyzeWritingSample = async (sampleData: WritingSampleRequest): Promise<WritingSampleResponse> => {
  return safeApiCall(async () => {
    const response = await apiClient.post('/api/writing/analyze-sample', sampleData);
    return response.data;
  });
};

export const completeOnboarding = async (onboardingData: OnboardingRequest): Promise<OnboardingResponse> => {
  return safeApiCall(async () => {
    const response = await apiClient.post('/api/writing/onboarding', onboardingData);
    return response.data;
  });
};

export const saveCheckpoint = async (checkpointData: CheckpointRequest): Promise<CheckpointResponse> => {
  return safeApiCall(async () => {
    const response = await apiClient.post('/api/writing/checkpoint', checkpointData);
    return response.data;
  });
};

// === CHAT UTILITY FUNCTIONS ===

export const buildChatRequest = (
  message: string,
  editorText: string,
  authorPersona: string,
  helpFocus: string,
  llmProvider: string,
  options?: {
    highlightedText?: string;
    highlightId?: string;
    chatHistory?: any[];
    userPreferences?: UserPreferences;
    feedbackOnPrevious?: string;
  }
): ChatRequest => {
  return {
    message,
    editor_text: editorText,
    highlighted_text: options?.highlightedText,
    highlight_id: options?.highlightId,
    author_persona: authorPersona,
    help_focus: helpFocus,
    chat_history: options?.chatHistory || [],
    llm_provider: llmProvider,
    user_preferences: options?.userPreferences,
    feedback_on_previous: options?.feedbackOnPrevious
  };
}; 
 