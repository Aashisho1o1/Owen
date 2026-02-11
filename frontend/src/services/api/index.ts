/**
 * API Services - Centralized Exports
 * Clean interface to all modular API services.
 * Replaces the monolithic api.ts file.
 */

// === RE-EXPORT ALL TYPES ===
export * from './types';

// === RE-EXPORT CLIENT UTILITIES ===
export { default as apiClient } from './client';

// === RE-EXPORT AUTHENTICATION SERVICES ===
export {
  loginUser,
  registerUser,
  refreshToken,
  getUserProfile,
  logoutUser,
  setAuthTokens,
  clearAuthTokens,
  getStoredTokens,
  isTokenExpired
} from './auth';

// === RE-EXPORT DOCUMENT SERVICES ===
export {
  getDocuments,
  getDocument,
  createDocument,
  updateDocument,
  deleteDocument,
  autoSaveDocument,
  // createDocumentFromTemplate removed - template system deprecated
  duplicateDocument,
  moveDocumentToFolder
} from './documents';

// === RE-EXPORT FOLDER SERVICES ===
export {
  getFolders,
  createFolder,
  updateFolder,
  deleteFolder,
  getFolderById,
  getFolderName,
  getSubfolders,
  getRootFolders
} from './folders';

// === TEMPLATE SERVICES REMOVED ===
// Template system deprecated for MVP simplicity

// === RE-EXPORT CHAT SERVICES ===
export {
  sendChatMessage,
  generateSuggestions,
  submitUserFeedback,
  getUserPreferences,
  acceptSuggestion,
  buildChatRequest
} from './chat';

// === RE-EXPORT SEARCH SERVICES ===
export {
  searchDocuments,
  searchDocumentsLocally,
  buildSearchRequest,
  highlightSearchMatches
} from './search';

// === CHARACTER VOICE CONSISTENCY SERVICES ===
export {
  analyzeVoiceConsistency,
  getCharacterProfiles,
  updateCharacterProfile,
  deleteCharacterProfile,
  checkCharacterVoiceHealth,
  hasDialogue,
  analyzeVoiceConsistencyDebounced,
  cancelPendingAnalysis
} from './character-voice';

// === HEALTH CHECK ===
import apiClient from './client';

export const checkApiHealth = async (): Promise<any> => {
  const response = await apiClient.get('/api/health');
  return response.data;
};

// Default export for convenience
export default apiClient;
 
