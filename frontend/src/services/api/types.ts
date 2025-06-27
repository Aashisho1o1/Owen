/**
 * API Types & Interfaces
 * Centralized type definitions for all API interactions.
 * Extracted from api.ts as part of God File refactoring.
 */

// === CHAT INTERFACES ===
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
  highlighted_text?: string;
  highlight_id?: string;
  author_persona: string;
  help_focus: string;
  chat_history: ChatMessage[];
  llm_provider: string;
  ai_mode: string;
  user_preferences?: UserPreferences;
  feedback_on_previous?: string;
  english_variant?: string;
}

export interface ChatResponse {
  dialogue_response: string;
  thinking_trail?: string;
}

// NEW: Enhanced types for AI suggestions feature
export interface SuggestionOption {
  id: string;
  text: string;
  type: string;
  confidence: number;
  explanation?: string;
}

export interface EnhancedChatResponse {
  dialogue_response: string;
  thinking_trail?: string;
  suggestions: SuggestionOption[];
  original_text?: string;
  has_suggestions: boolean;
}

export interface AcceptSuggestionRequest {
  suggestion_id: string;
  original_text: string;
  suggested_text: string;
  editor_content: string;
  position_info?: any;
}

export interface AcceptSuggestionResponse {
  success: boolean;
  updated_content: string;
  replacement_info?: {
    original_text: string;
    suggested_text: string;
    suggestion_id: string;
  };
  error?: string;
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

// === DOCUMENT INTERFACES ===
export interface Document {
  id: string;
  title: string;
  content: string;
  created_at: string;
  updated_at: string;
  user_id: string;
  is_favorite?: boolean;
  word_count?: number;
  folder_id?: string;
  tags?: string[];
  document_type?: 'novel' | 'chapter' | 'character_sheet' | 'outline' | 'notes';
}

export interface DocumentFolder {
  id: string;
  name: string;
  parent_id?: string;
  user_id: string;
  created_at: string;
  color?: string;
  icon?: string;
  document_count?: number;
}

export interface DocumentTemplate {
  id: string;
  name: string;
  content: string;
  document_type: string;
  is_system: boolean;
  user_id?: string;
  preview_text: string;
}

export interface SearchRequest {
  query: string;
  document_ids?: string[];
  folder_ids?: string[];
  tags?: string[];
  document_types?: string[];
  content_only?: boolean;
}

export interface SearchResult {
  document_id: string;
  document_title: string;
  matches: {
    content: string;
    context: string;
    position: number;
  }[];
  relevance_score: number;
}

export interface CreateDocumentRequest {
  title: string;
  content?: string;
  document_type?: string;
  folder_id?: string;
}

export interface UpdateDocumentRequest {
  id: string;
  title?: string;
  content?: string;
  is_favorite?: boolean;
  tags?: string[];
}

export interface DocumentsResponse {
  documents: Document[];
  total: number;
}

export interface CreateFolderRequest {
  name: string;
  parent_id?: string;
  color?: string;
}

export interface CreateFromTemplateRequest {
  template_id: string;
  title: string;
  folder_id?: string;
}

// === AUTHENTICATION INTERFACES ===
export interface LoginRequest {
  username: string;
  password: string;
}

export interface RegisterRequest {
  username: string;
  name: string;
  email: string;
  password: string;
}

export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
}

export interface UserProfile {
  id: number;
  username: string;
  name: string;
  email: string;
}

// Explicit module termination to ensure proper CodeQL parsing
export {}; 