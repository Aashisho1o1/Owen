/**
 * API Client Configuration
 * Centralized HTTP client setup with authentication and error handling.
 * Extracted from api.ts as part of God File refactoring.
 */

import axios, { AxiosInstance, AxiosError } from 'axios';

// Get API URL from environment variable or fallback to production
const rawApiUrl = import.meta.env.VITE_API_URL || 'https://backend-copy-production-95b5.up.railway.app';
const API_URL = rawApiUrl.startsWith('http') ? rawApiUrl : `https://${rawApiUrl}`;

// Debug logging for API configuration
console.log('🌐 API Configuration:', {
  VITE_API_URL: import.meta.env.VITE_API_URL,
  rawApiUrl,
  API_URL,
  mode: import.meta.env.MODE
});

// Enhanced error handler for better debugging
const handleApiError = (error: AxiosError): never => {
  const errorContext = {
    url: error.config?.url,
    method: error.config?.method,
    status: error.response?.status,
    statusText: error.response?.statusText,
    data: error.response?.data,
    message: error.message,
    code: error.code
  };

  console.error('❌ API Error Details:', errorContext);

  // Enhanced error message for user
  let userMessage = 'An unexpected error occurred. Please try again.';
  
  if (error.code === 'ECONNREFUSED' || error.message.includes('Network Error')) {
    userMessage = 'Unable to connect to the server. Please check if the backend is running.';
  } else if (error.response?.status === 500) {
    userMessage = 'Server error occurred. Please try again later.';
  } else if (error.response?.status === 404) {
    userMessage = 'API endpoint not found. Please check your configuration.';
  } else if (error.response?.status === 401) {
    userMessage = 'Authentication failed. Please log in again.';
  } else if (error.response?.status === 403) {
    userMessage = 'Access denied. You do not have permission for this action.';
  } else if (error.response?.data) {
    const responseData = error.response.data as any;
    userMessage = responseData?.detail || responseData?.error || responseData?.message || userMessage;
  }

  // Add user-friendly message to error object
  (error as any).userMessage = userMessage;
  throw error;
};

// Create axios instance with authentication support
const apiClient: AxiosInstance = axios.create({
  baseURL: API_URL,
  timeout: 25000, // Increased timeout to 25s for Gemini models
  headers: {
    'Content-Type': 'application/json',
    'X-Requested-With': 'XMLHttpRequest',
  },
});

// Add authentication token to requests
apiClient.interceptors.request.use(
  (config) => {
    // Add authentication token if available
    const token = localStorage.getItem('owen_access_token');
    const tokenType = localStorage.getItem('owen_token_type') || 'bearer';
    
    if (token && !config.headers['Authorization']) {
      config.headers['Authorization'] = `${tokenType} ${token}`;
    }
    
    console.log(`🔄 API Request: ${config.method?.toUpperCase()} ${config.url}`);
    console.log('Request data:', config.data);
    return config;
  },
  (error) => {
    console.error('❌ Request Error:', error);
    return Promise.reject(error);
  }
);

apiClient.interceptors.response.use(
  (response) => {
    console.log(`✅ API Response: ${response.config.method?.toUpperCase()} ${response.config.url} - ${response.status}`);
    return response;
  },
  (error: AxiosError) => {
    return Promise.reject(handleApiError(error));
  }
);

// Type-safe wrapper for API calls
export const safeApiCall = async <T>(apiCall: () => Promise<T>): Promise<T> => {
  try {
    return await apiCall();
  } catch (error) {
    console.error('🔍 Detailed error analysis:', {
      errorName: error?.constructor?.name,
      errorMessage: (error as Error)?.message,
      errorStack: (error as Error)?.stack,
      apiUrl: API_URL,
      hasRequest: !!(error as any)?.config,
      hasResponse: !!(error as any)?.response,
      responseStatus: (error as any)?.response?.status,
      responseData: (error as any)?.response?.data,
      timestamp: new Date().toISOString()
    });
    throw error;
  }
};

// Export the configured client and API URL
export { apiClient, API_URL }; 
 