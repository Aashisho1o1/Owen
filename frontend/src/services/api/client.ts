/**
 * API Client Configuration
 * Centralized HTTP client setup with authentication and error handling.
 * Extracted from api.ts as part of God File refactoring.
 */

import axios, { AxiosInstance, AxiosRequestConfig, AxiosResponse, InternalAxiosRequestConfig } from 'axios';
import { clearAuthTokens, getStoredTokens, refreshToken } from './auth';
import { logger } from '../utils/logger';

// Use VITE_API_URL from environment variables, with a fallback for local development
const API_URL = import.meta.env.VITE_API_URL;

console.log('🌐 API Configuration:', {
  VITE_API_URL: import.meta.env.VITE_API_URL,
  API_URL,
  NODE_ENV: import.meta.env.NODE_ENV
});

// Create axios instance with configuration
const apiClient = axios.create({
  baseURL: API_URL,
  timeout: 30000, // Default 30 seconds
  headers: {
    'Content-Type': 'application/json',
  },
});

// Special timeout for voice analysis (Gemini can be slow)
const VOICE_ANALYSIS_TIMEOUT = 60000; // 60 seconds for voice analysis

// Token refresh state management
let isRefreshing = false;
let failedQueue: Array<{
  resolve: (value: any) => void;
  reject: (error: any) => void;
}> = [];

const processQueue = (error: any, token: string | null = null) => {
  failedQueue.forEach(({ resolve, reject }) => {
    if (error) {
      reject(error);
    } else {
      resolve(token);
    }
  });
  
  failedQueue = [];
};

const refreshTokens = async (): Promise<string | null> => {
  const { refreshToken } = getStoredTokens();
  
  if (!refreshToken) {
    throw new Error('No refresh token available');
  }

  try {
    console.log('🔄 Refreshing tokens with stored refresh token');
    
    // Use a fresh axios instance to avoid interceptor loops
    const response = await axios.post(`${API_URL}/api/auth/refresh`, {
      refresh_token: refreshToken
    }, {
      headers: {
        'Content-Type': 'application/json'
      }
    });

    const { access_token, refresh_token: newRefreshToken, token_type, expires_in } = response.data;
    
    console.log('✅ Token refresh successful, storing new tokens');
    
    // Store new tokens with CONSISTENT owen_ prefix
    localStorage.setItem('owen_access_token', access_token);
    localStorage.setItem('owen_refresh_token', newRefreshToken);
    localStorage.setItem('owen_token_type', token_type);
    localStorage.setItem('owen_token_expires', (Date.now() + expires_in * 1000).toString());
    
    return access_token;
  } catch (error) {
    console.error('❌ Token refresh failed:', error);
    
    // COMPREHENSIVE token cleanup - remove all possible token keys
    const tokenKeys = [
      'owen_access_token',
      'owen_refresh_token', 
      'owen_token_type',
      'owen_token_expires',
      // Legacy keys without prefix
      'access_token',
      'refresh_token',
      'token_type',
      'expires_at'
    ];
    
    tokenKeys.forEach(key => localStorage.removeItem(key));
    console.log('🧹 All tokens cleared after refresh failure');
    
    throw error;
  }
};

// Request interceptor
apiClient.interceptors.request.use(
  (config) => {
    console.log(`🚀 API Request: ${config.method?.toUpperCase()} ${config.url}`);
    
    // Special handling for voice analysis endpoints
    if (config.url?.includes('/character-voice/analyze')) {
      console.log('🧠 Voice Analysis Request: Using extended timeout (60s)');
      console.log('⏳ Processing with Gemini AI - this may take 30-60 seconds...');
      config.timeout = VOICE_ANALYSIS_TIMEOUT;
    }
    
    const token = getStoredTokens().accessToken;
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor to handle 401 errors with token refresh
apiClient.interceptors.response.use(
  (response: AxiosResponse) => {
    return response;
  },
  async (error) => {
    const originalRequest = error.config;
    
    // Handle 401 errors with token refresh
    if (error.response?.status === 401 && !originalRequest._retry) {
      if (isRefreshing) {
        // If already refreshing, queue this request
        return new Promise((resolve, reject) => {
          failedQueue.push({ resolve, reject });
        }).then((token) => {
          originalRequest.headers.Authorization = `Bearer ${token}`;
          return apiClient(originalRequest);
        }).catch((err) => {
          return Promise.reject(err);
        });
      }

      originalRequest._retry = true;
      isRefreshing = true;

      try {
        console.log('🔄 Attempting token refresh...');
        const newToken = await refreshTokens();
        
        processQueue(null, newToken);
        isRefreshing = false;
        
        // Retry original request with new token
        originalRequest.headers.Authorization = `Bearer ${newToken}`;
        return apiClient(originalRequest);
        
      } catch (refreshError) {
        console.log('🔐 Token refresh failed - logging out user');
        
        processQueue(refreshError, null);
        isRefreshing = false;
        
        // COMPREHENSIVE token cleanup - same as refreshTokens function
        const tokenKeys = [
          'owen_access_token',
          'owen_refresh_token', 
          'owen_token_type',
          'owen_token_expires',
          // Legacy keys without prefix
          'access_token',
          'refresh_token',
          'token_type',
          'expires_at'
        ];
        
        tokenKeys.forEach(key => localStorage.removeItem(key));
        console.log('🧹 All tokens cleared after interceptor refresh failure');
        
        // Dispatch token expired event ONLY once
        window.dispatchEvent(new CustomEvent('auth:token-expired'));
        
        throw new Error('🔐 Authentication required. Please sign in again to continue using the AI Writing Assistant.');
      }
    }
    
    // Handle other HTTP errors
    if (error.response) {
      console.error('❌ API Error:', error.response.status, error.response.data);
      throw error;
    } else if (error.request) {
      console.error('❌ Network Error:', error.message);
      throw new Error('Network error. Please check your connection and try again.');
    } else {
      console.error('❌ Request Error:', error.message);
      throw error;
    }
  }
);

export default apiClient; 