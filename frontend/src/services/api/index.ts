/**
 * API Services - Centralized Exports
 * Clean interface to all modular API services.
 * Replaces the monolithic api.ts file.
 */

// === RE-EXPORT ALL TYPES ===
export * from './types';

// === RE-EXPORT CLIENT UTILITIES ===
export { apiClient, API_URL, safeApiCall } from './client';

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
  createDocumentFromTemplate,
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

// === RE-EXPORT TEMPLATE SERVICES ===
export {
  getTemplates,
  getTemplate,
  getTemplateById,
  getTemplatesByCategory,
  getSystemTemplates,
  getUserTemplates
} from './templates';

// === RE-EXPORT CHAT SERVICES ===
export {
  sendChatMessage,
  submitUserFeedback,
  getUserPreferences,
  analyzeWritingSample,
  completeOnboarding,
  saveCheckpoint,
  buildChatRequest
} from './chat';

// === RE-EXPORT SEARCH SERVICES ===
export {
  searchDocuments,
  searchDocumentsLocally,
  buildSearchRequest,
  highlightSearchMatches
} from './search';

// === LEGACY COMPATIBILITY ===
// For components that still import from the old api.ts path
// TODO: Update all imports to use specific services and remove this section

// Health check endpoint (keeping in main client for simplicity)
export const checkApiHealth = async (): Promise<any> => {
  return safeApiCall(async () => {
    const response = await apiClient.get('/api/health');
    return response.data;
  });
};
 