/**
 * API Client Configuration
 * Centralized HTTP client setup with authentication and error handling.
 * Extracted from api.ts as part of God File refactoring.
 */

import axios, { AxiosInstance, AxiosRequestConfig, AxiosError } from 'axios';

// Base URL configuration
const baseURL = import.meta.env.VITE_API_URL || 'https://backend-copy-production-95b5.up.railway.app';

console.log('🌐 API Configuration:', {
  baseURL,
  environment: import.meta.env.MODE,
  apiUrl: import.meta.env.VITE_API_URL
});

// Create axios instance
const apiClient: AxiosInstance = axios.create({
  baseURL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Token management
const getStoredTokens = () => {
  const accessToken = localStorage.getItem('access_token') || localStorage.getItem('owen_access_token');
  const refreshToken = localStorage.getItem('refresh_token') || localStorage.getItem('owen_refresh_token');
  return { accessToken, refreshToken };
};

// Request interceptor
apiClient.interceptors.request.use(
  (config) => {
    const { accessToken } = getStoredTokens();
    if (accessToken) {
      config.headers.Authorization = `Bearer ${accessToken}`;
    }
    
    console.log(`🚀 API Request: ${config.method?.toUpperCase()} ${config.url}`);
    return config;
  },
  (error) => {
    console.error('❌ Request interceptor error:', error);
    return Promise.reject(error);
  }
);

// Response interceptor
apiClient.interceptors.response.use(
  (response) => {
    return response;
  },
  async (error) => {
    // Handle 401 errors immediately
    if (error.response?.status === 401) {
      console.log('🔐 401 Unauthorized - clearing tokens');
      
      // Clear all tokens
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      localStorage.removeItem('token');
      localStorage.removeItem('authToken');
      localStorage.removeItem('owen_access_token');
      localStorage.removeItem('owen_refresh_token');
      
      // Dispatch token expired event
      window.dispatchEvent(new CustomEvent('auth:token-expired'));
      
      throw new Error('🔐 Authentication required. Please sign in again to continue using the AI Writing Assistant.');
    }
    
    // Handle other HTTP errors
    if (error.response) {
      const status = error.response.status;
      const message = error.response.data?.detail || error.response.data?.message || `HTTP ${status} Error`;
      
      if (status === 403) {
        throw new Error('🚫 Access forbidden. You do not have permission to access this resource.');
      } else if (status === 404) {
        throw new Error('🔍 Resource not found. The requested item may have been deleted or moved.');
      } else if (status === 422) {
        throw new Error('📝 Invalid data provided. Please check your input and try again.');
      } else if (status === 429) {
        throw new Error('⏰ Too many requests. Please wait a moment and try again.');
      } else if (status >= 500) {
        throw new Error('🔧 Server error. Our team has been notified. Please try again later.');
      } else {
        throw new Error(message);
      }
    }
    
    // Handle network errors
    if (error.request) {
      console.error('❌ Network Error - No response received:', error.message);
      throw new Error('🌐 Network error. Please check your internet connection and try again.');
    }
    
    // Handle other errors
    throw new Error(`⚠️ Request failed: ${error.message}`);
  }
);

export { apiClient };
export default apiClient; 