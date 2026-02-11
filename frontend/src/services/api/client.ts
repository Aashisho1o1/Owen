/**
 * API Client Configuration
 * Centralized HTTP client setup with authentication and error handling.
 * Extracted from api.ts as part of God File refactoring.
 */

import axios, { AxiosResponse } from 'axios';
import { getStoredTokens } from './auth';

// Use VITE_API_URL from environment variables - MUST be defined in .env file
// Normalize API_URL to prevent double slashes (trailing slash issues)
const API_URL = import.meta.env.VITE_API_URL?.replace(/\/+$/, '') || '';

// Validate environment variable is loaded
if (!API_URL) {
  console.error('❌ CRITICAL: VITE_API_URL is not defined in environment variables');
  console.error('Please ensure your .env file contains VITE_API_URL=your_backend_url');
  throw new Error('VITE_API_URL environment variable is required but not defined');
}

console.log('🌐 API Configuration:', {
  VITE_API_URL: import.meta.env.VITE_API_URL,
  API_URL,
  NODE_ENV: import.meta.env.NODE_ENV,
  env_loaded: !!import.meta.env.VITE_API_URL
});

// Development safety check for double slashes
if (import.meta.env.DEV && import.meta.env.VITE_API_URL?.endsWith('/')) {
  console.warn('⚠️ VITE_API_URL ends with trailing slash. This has been auto-corrected to prevent double-slash issues.');
  console.warn('💡 Recommendation: Remove trailing slash from VITE_API_URL in your .env file');
}

// Create axios instance with configuration
const apiClient = axios.create({
  baseURL: API_URL,
  timeout: 30000, // Default 30 seconds
  headers: {
    'Content-Type': 'application/json',
  },
});

// Special timeout for voice analysis (Gemini 2.5 Flash can be slow for complex analysis)
const VOICE_ANALYSIS_TIMEOUT = 300000; // 5 minutes for voice analysis with buffer

// Token refresh state management
let isRefreshing = false;
let failedQueue: Array<{
  resolve: (value: unknown) => void;
  reject: (error: unknown) => void;
}> = [];

const processQueue = (error: unknown, token: string | null = null) => {
  failedQueue.forEach(({ resolve, reject }) => {
    if (error) {
      reject(error);
    } else {
      resolve(token);
    }
  });
  
  failedQueue = [];
};

// CRITICAL FIX: Token synchronization function
export const updateApiClientToken = (token: string | null, tokenType: string = 'Bearer') => {
  console.log('🔄 Updating apiClient token:', token ? 'Token set' : 'Token cleared');
  if (token) {
    apiClient.defaults.headers.common['Authorization'] = `${tokenType} ${token}`;
  } else {
    delete apiClient.defaults.headers.common['Authorization'];
  }
};

const refreshTokens = async (): Promise<string | null> => {
  const { refreshToken: storedRefreshToken } = getStoredTokens();
  
  if (!storedRefreshToken) {
    throw new Error('No refresh token available');
  }

  try {
    console.log('🔄 Refreshing tokens with stored refresh token');
    
    // Use a fresh axios instance to avoid interceptor loops
    const response = await axios.post(`${API_URL}/api/auth/refresh`, {
      refresh_token: storedRefreshToken
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
    
    // CRITICAL: Update apiClient with new token
    updateApiClientToken(access_token, token_type);
    
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
    
    // CRITICAL: Clear token from apiClient
    updateApiClientToken(null);
    
    throw error;
  }
};

// Request interceptor
apiClient.interceptors.request.use(
  (config) => {
    console.log(`🚀 API Request: ${config.method?.toUpperCase()} ${config.url}`);
    
    // Development safety check for double slashes in URLs
    if (import.meta.env.DEV && config.url?.includes('//api/')) {
      console.error('🚨 DOUBLE SLASH DETECTED in API URL:', config.url);
      console.error('💡 This usually indicates a trailing slash issue in VITE_API_URL');
      console.error('🔧 Expected URL pattern: baseURL + /api/... (no double slashes)');
    }
    
    // Special handling for voice analysis endpoints - ALWAYS bypass deduplication
    if (config.url?.includes('/character-voice/analyze')) {
      console.log('🧠 Voice Analysis Request: Using extended timeout (5 minutes)');
      console.log('🚀 Starting Gemini 2.5 Flash analysis...');
      console.log('⏳ Processing with Gemini 2.5 Flash - this may take 1-4 minutes for complex dialogue analysis...');
      console.log('💡 Please wait - analyzing character voice consistency...');
      config.timeout = VOICE_ANALYSIS_TIMEOUT;
      
      // Ensure fresh headers for voice analysis
      config.headers = { 
        ...config.headers,
        'X-Fresh-Request': Date.now().toString()
      };
    }
    
    const storedTokens = getStoredTokens();
    if (storedTokens.accessToken) {
      // Check if token is expired before making the request
      if (storedTokens.expiresAt && Date.now() >= storedTokens.expiresAt) {
        console.log('⏰ Token expired before request, should refresh');
        // Note: We don't refresh here to avoid blocking the request interceptor
        // The response interceptor will handle the 401/403 and refresh
      }
      config.headers.Authorization = `Bearer ${storedTokens.accessToken}`;
    } else {
      // DEBUG: Log when no token is available
      console.log('⚠️ No access token available for request:', config.url);
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor for centralized API error logging
apiClient.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    // ENHANCED: Log the specific error for debugging
    if (error.response) {
      console.error(`❌ API Error ${error.response.status}:`, {
        url: error.config?.url,
        method: error.config?.method,
        status: error.response.status,
        statusText: error.response.statusText,
        data: error.response.data
      });
    }
    
    return Promise.reject(error);
  }
);

// Response interceptor to handle 401 errors with token refresh
apiClient.interceptors.response.use(
  (response: AxiosResponse) => {
    return response;
  },
  async (error) => {
    const originalRequest = error.config;
    
    // Handle 401 AND 403 errors with token refresh
    if ((error.response?.status === 401 || error.response?.status === 403) && !originalRequest._retry) {
      // CRITICAL FIX: Check if we have a token before attempting refresh
      // This prevents logout loops for unauthenticated users
      const storedTokens = getStoredTokens();
      if (!storedTokens.accessToken) {
        // No token exists = user hasn't authenticated yet, this is expected behavior
        console.log(`🔒 Got ${error.response?.status} but no token exists - user needs to authenticate first`);
        // IMPORTANT: Don't trigger logout event - user was never logged in!
        return Promise.reject(error);
      }
      
      // CRITICAL FIX: Add refresh token guard for guest sessions
      // Guest sessions have access tokens but no refresh tokens
      if (!storedTokens.refreshToken) {
        console.log('🧑‍🚀 Guest session detected (no refresh token) - skipping token refresh');
        return Promise.reject(error);
      }
      
      // CRITICAL: Don't attempt token refresh for auth endpoints to prevent infinite loops
      const isAuthEndpoint = originalRequest.url && (
        originalRequest.url.includes('/api/auth/login') ||
        originalRequest.url.includes('/api/auth/register') ||
        originalRequest.url.includes('/api/auth/refresh')
      );

      if (isAuthEndpoint) {
        console.log(`🚫 Skipping token refresh for auth endpoint: ${originalRequest.url}`);
        return Promise.reject(error);
      }

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
        console.log(`🔄 Attempting token refresh for ${error.response?.status === 403 ? '403 Forbidden' : '401 Unauthorized'}...`);
        const newToken = await refreshTokens();
        
        processQueue(null, newToken);
        isRefreshing = false;
        
        // Retry original request with new token
        originalRequest.headers.Authorization = `Bearer ${newToken}`;
        console.log('✅ Token refreshed, retrying original request');
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
        
        // CRITICAL: Clear token from apiClient
        updateApiClientToken(null);
        
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
