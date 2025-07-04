/**
 * API Services - Legacy Compatibility Layer
 * 
 * This file now re-exports everything from our new modular API structure.
 * The original 515-line God file has been refactored into 9 focused modules.
 */

// Re-export everything from the new modular API structure
export * from './api/index';

// Import everything for the default export
import * as apiServices from './api/index';

// Default export for backward compatibility with existing imports
const api = {
  // Health check
  healthCheck: apiServices.checkApiHealth,
  
  // Authentication
  login: apiServices.loginUser,
  register: apiServices.registerUser,
  refreshToken: apiServices.refreshToken,
  getUserProfile: apiServices.getUserProfile,
  logout: apiServices.logoutUser,
  
  // Documents
  getDocuments: apiServices.getDocuments,
  getDocument: apiServices.getDocument,
  createDocument: apiServices.createDocument,
  updateDocument: apiServices.updateDocument,
  deleteDocument: apiServices.deleteDocument,
  autoSaveDocument: apiServices.autoSaveDocument,
  createDocumentFromTemplate: apiServices.createDocumentFromTemplate,
  duplicateDocument: apiServices.duplicateDocument,
  
  // Folders
  getFolders: apiServices.getFolders,
  createFolder: apiServices.createFolder,
  updateFolder: apiServices.updateFolder,
  deleteFolder: apiServices.deleteFolder,
  
  // Templates
  getTemplates: apiServices.getTemplates,
  getTemplate: apiServices.getTemplate,
  
  // Chat
  sendChatMessage: apiServices.sendChatMessage,
  submitUserFeedback: apiServices.submitUserFeedback,
  getUserPreferences: apiServices.getUserPreferences,
  generateSuggestions: apiServices.generateSuggestions,
  acceptSuggestion: apiServices.acceptSuggestion,
  
  // Search
  searchDocuments: apiServices.searchDocuments,
  
  // Utilities
  setAuthTokens: apiServices.setAuthTokens,
  clearAuthTokens: apiServices.clearAuthTokens,
  getStoredTokens: apiServices.getStoredTokens,
  isTokenExpired: apiServices.isTokenExpired
};

export default api;
