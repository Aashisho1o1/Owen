/**
 * Chat API Service
 * Handles all chat-related API calls.
 * Extracted from api.ts as part of God File refactoring.
 */

import apiClient from './client';
import { ChatRequest, ChatResponse, EnhancedChatResponse, UserFeedbackRequest } from './types';

// === CHAT ENDPOINTS ===

export const sendChatMessage = async (request: ChatRequest): Promise<ChatResponse> => {
  // OPTIMIZED FIX: Reduced timeout for better user experience.
  // VoiceGuard requests may run longer; standard requests should fail fast.
  const timeoutMs = request.voice_guard ? 150000 : 45000; // 2.5 min vs 45 sec
  
  console.log(`🔧 Chat request timeout: ${timeoutMs/1000}s (VoiceGuard: ${request.voice_guard})`);
  console.log(`🔧 Premium features enabled: VoiceGuard=${request.voice_guard}`);
  
  // ENHANCED DEBUGGING: Check authentication state before request
  const tokens = localStorage.getItem('owen_access_token');
  const expiresAt = localStorage.getItem('owen_token_expires');
  const isExpired = expiresAt ? Date.now() >= parseInt(expiresAt) : true;
  
  console.log('🔐 Authentication Debug:', {
    hasToken: !!tokens,
    tokenLength: tokens ? tokens.length : 0,
    isExpired,
    expiresAt: expiresAt ? new Date(parseInt(expiresAt)).toISOString() : 'none'
  });
  
  // ENHANCED DEBUGGING: Log request details
  console.log('📤 Chat Request Details:', {
    url: '/api/chat/',
    method: 'POST',
    timeout: timeoutMs,
    hasToken: !!tokens,
    voiceGuard: request.voice_guard,
    messagePreview: request.message.substring(0, 50) + '...'
  });

  // ENHANCED: Add progress feedback for long operations
  if (request.voice_guard) {
    // Emit progress events for UI feedback
    window.dispatchEvent(new CustomEvent('folderScopeProgress', { 
      detail: { stage: 'starting', message: 'Running voice analysis...' } 
    }));
  }

  try {
    console.log('📡 Sending request to backend...');
    const response = await apiClient.post('/api/chat/', request, { 
      timeout: timeoutMs,
      headers: {
        'Content-Type': 'application/json',
        'X-Request-Type': request.voice_guard ? 'voice-guard' : 'standard',
        'X-Debug-Features': JSON.stringify({
          voiceGuard: request.voice_guard
        })
      },
    });
    
    console.log('✅ Chat response received:', {
      status: response.status,
      hasDialogue: !!response.data.dialogue_response,
      hasThinking: !!response.data.thinking_trail,
      responseLength: response.data.dialogue_response?.length || 0
    });
    
    // On success, clear any progress messages
    if (request.voice_guard) {
      window.dispatchEvent(new CustomEvent('folderScopeProgress', { detail: { stage: 'completed' } }));
    }
    return response.data;
  } catch (error: any) {
    console.error('❌ Chat request failed:', {
      status: error.response?.status,
      statusText: error.response?.statusText,
      message: error.message,
      url: error.config?.url,
      headers: error.config?.headers,
      timeout: error.code === 'ECONNABORTED' && error.message.includes('timeout')
    });
    
    // On error, clear any progress messages and show error
    if (request.voice_guard) {
      window.dispatchEvent(new CustomEvent('folderScopeProgress', { 
        detail: { 
          stage: 'error', 
          message: `Request failed: ${error.response?.status || error.message}` 
        } 
      }));
    }
    
    // ENHANCED ERROR DEBUGGING: Log specific error details
    if (error.response?.status === 401 || error.response?.status === 403) {
      console.error('🔐 Authentication Error Details:', {
        status: error.response.status,
        data: error.response.data,
        headers: error.response.headers,
        hasToken: !!tokens,
        tokenExpired: isExpired
      });
    }
    
    throw error; // Re-throw the error for further handling
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
  aiMode: string = 'talk',
  voiceGuard: boolean = false
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
    ai_mode: aiMode,
    // Include premium feature flags in request
    voice_guard: voiceGuard
  };
};
