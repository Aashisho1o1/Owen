/**
 * API Client Configuration
 * Centralized HTTP client setup with authentication and error handling.
 * Extracted from api.ts as part of God File refactoring.
 */

import axios, { AxiosInstance, AxiosError, AxiosRequestConfig } from 'axios';
import { getStoredTokens, clearAuthTokens } from './auth';

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

// Enhanced retry configuration
interface RetryConfig {
  retries: number;
  retryDelay: (retryCount: number) => number;
  retryCondition: (error: AxiosError) => boolean;
  onRetry?: (error: AxiosError, retryCount: number) => void;
}

const defaultRetryConfig: RetryConfig = {
  retries: 3,
  retryDelay: (retryCount) => Math.min(1000 * Math.pow(2, retryCount), 10000),
  retryCondition: (error) => {
    // Retry on network errors or 5xx status codes
    return !error.response || (error.response.status >= 500 && error.response.status < 600);
  },
  onRetry: (error, retryCount) => {
    console.log(`Retry attempt ${retryCount} after error:`, error.message);
  }
};

// Create axios instance with enhanced configuration
export const apiClient: AxiosInstance = axios.create({
  baseURL: API_URL,
  timeout: 30000, // 30 seconds
  headers: {
    'Content-Type': 'application/json',
  },
  validateStatus: (status) => status < 500, // Don't throw on 4xx errors
});

// Request interceptor with retry logic
let isRefreshing = false;
let failedQueue: Array<{
  resolve: (value?: any) => void;
  reject: (reason?: any) => void;
}> = [];

const processQueue = (error: any, token: string | null = null) => {
  failedQueue.forEach((prom) => {
    if (error) {
      prom.reject(error);
    } else {
      prom.resolve(token);
    }
  });
  failedQueue = [];
};

// Implement retry logic
async function retryRequest(
  error: AxiosError,
  retryConfig: RetryConfig = defaultRetryConfig
): Promise<any> {
  const config = error.config as AxiosRequestConfig & { _retry?: number };
  
  if (!config || !retryConfig.retryCondition(error)) {
    return Promise.reject(error);
  }

  config._retry = config._retry || 0;

  if (config._retry >= retryConfig.retries) {
    return Promise.reject(error);
  }

  config._retry += 1;

  if (retryConfig.onRetry) {
    retryConfig.onRetry(error, config._retry);
  }

  await new Promise(resolve => setTimeout(resolve, retryConfig.retryDelay(config._retry)));

  return apiClient(config);
}

apiClient.interceptors.request.use(
  (config) => {
    // Add auth token
    const { accessToken } = getStoredTokens();
    if (accessToken) {
      config.headers.Authorization = `Bearer ${accessToken}`;
    }

    // Add request ID for tracking
    config.headers['X-Request-ID'] = `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
    
    // Log request for debugging
    console.log(`🚀 API Request: ${config.method?.toUpperCase()} ${config.url}`);
    
    return config;
  },
  (error) => {
    console.error('❌ Request interceptor error:', error);
    return Promise.reject(error);
  }
);

// Response interceptor with retry logic
apiClient.interceptors.response.use(
  (response) => {
    console.log(`✅ API Response: ${response.config.url} - Status: ${response.status}`);
    return response;
  },
  async (error: AxiosError) => {
    const originalRequest = error.config as AxiosRequestConfig & { _retry?: boolean };

    // CRITICAL FIX: Log the actual error details before any processing
    console.error(`❌ API Error: ${error.config?.url} - Status: ${error.response?.status || 'undefined'}`);
    console.error('❌ Full Error Details:', {
      message: error.message,
      code: error.code,
      status: error.response?.status,
      statusText: error.response?.statusText,
      data: error.response?.data,
      hasResponse: !!error.response,
      hasRequest: !!error.request
    });

    // Handle 401 errors (token refresh) - but preserve original error if refresh fails
    if (error.response?.status === 401 && !originalRequest._retry) {
      console.log('🔐 401 Error detected, checking if we should try token refresh...');
      
      if (isRefreshing) {
        console.log('🔄 Already refreshing, queuing request...');
        return new Promise((resolve, reject) => {
          failedQueue.push({ resolve, reject });
        }).then(() => apiClient(originalRequest));
      }

      originalRequest._retry = true;
      isRefreshing = true;

      try {
        const { refreshToken } = getStoredTokens();
        if (refreshToken) {
          console.log('🔄 Attempting token refresh...');
          // Try to refresh token
          const response = await apiClient.post('/api/auth/refresh', {
            refresh_token: refreshToken
          });
          
          const { access_token } = response.data;
          localStorage.setItem('owen_access_token', access_token);
          
          console.log('✅ Token refresh successful, retrying original request');
          processQueue(null, access_token);
          return apiClient(originalRequest);
        } else {
          console.log('❌ No refresh token available, cannot refresh');
          throw new Error('No refresh token available');
        }
      } catch (refreshError) {
        console.error('❌ Token refresh failed:', refreshError);
        processQueue(refreshError, null);
        
        // CRITICAL FIX: Clear tokens and dispatch auth event but preserve original 401 error
        clearAuthTokens();
        
        console.log('📢 Dispatching auth:token-expired event due to refresh failure...');
        window.dispatchEvent(new CustomEvent('auth:token-expired', {
          detail: { 
            reason: 'Token refresh failed', 
            status: 401,
            originalError: error,
            refreshError 
          }
        }));
        
        // IMPORTANT: Return the original 401 error, not the refresh error
        // This ensures the UI gets the proper "Authentication required" message
        return Promise.reject(error);
      } finally {
        isRefreshing = false;
      }
    }

    // Retry logic for other errors (NOT for 401s)
    if (!originalRequest._retry && error.response?.status !== 401) {
      console.log(`🔄 Attempting retry for ${error.response?.status || 'network'} error...`);
      return retryRequest(error);
    }

    // CRITICAL: For 401 errors that we couldn't refresh, or any other errors, return as-is
    console.error('❌ Returning error without retry:', {
      status: error.response?.status,
      message: error.message,
      isRetry: !!originalRequest._retry
    });
    
    return Promise.reject(error);
  }
);

// Enhanced error handler for better debugging
const handleApiError = (error: AxiosError): never => {
  const errorContext = {
    url: error.config?.url,
    method: error.config?.method,
    status: error.response?.status,
    statusText: error.response?.statusText,
    data: error.response?.data,
    message: error.message,
    code: error.code,
    // Enhanced debugging information
    headers: error.response?.headers,
    requestHeaders: error.config?.headers,
    timeout: error.config?.timeout,
    baseURL: error.config?.baseURL
  };

  console.error('❌ API Error Details:', errorContext);

  // Enhanced error message for user with debugging info
  let userMessage = 'An unexpected error occurred. Please try again.';
  let debugInfo = '';
  
  if (error.response) {
    // Server responded with error status
    const status = error.response.status;
    const data = error.response.data as any;
    
    switch (status) {
      case 401:
        userMessage = '🔐 Authentication required. Please sign in again to continue using the AI Writing Assistant.';
        debugInfo = 'Invalid or expired authentication token';
        
        // ENHANCED: Clear ALL stored tokens on 401
        console.log('🧹 Clearing expired authentication tokens...');
        localStorage.removeItem('owen_access_token');
        localStorage.removeItem('owen_refresh_token');
        localStorage.removeItem('owen_token_type');
        localStorage.removeItem('owen_token_expires');
        
        // Also clear any legacy tokens that might exist
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        localStorage.removeItem('token_type');
        localStorage.removeItem('token_expires');
        
        // Dispatch event to notify auth context
        console.log('📢 Dispatching auth:token-expired event...');
        window.dispatchEvent(new CustomEvent('auth:token-expired', {
          detail: { reason: 'Invalid or expired token', status: 401 }
        }));
        break;
        
      case 403:
        userMessage = '🚫 Access denied. You don\'t have permission for this action.';
        debugInfo = 'Forbidden - insufficient permissions';
        break;
        
      case 404:
        userMessage = '🔍 The requested resource was not found.';
        debugInfo = `Resource not found: ${error.config?.url}`;
        break;
        
      case 422:
        userMessage = '📝 Invalid data provided. Please check your input and try again.';
        debugInfo = data?.detail || 'Validation error';
        break;
        
      case 429:
        userMessage = '⏳ Too many requests. Please wait a moment and try again.';
        debugInfo = 'Rate limit exceeded';
        break;
        
      case 500:
        userMessage = '🔧 Server error. Please try again in a moment.';
        debugInfo = 'Internal server error';
        break;
        
      default:
        userMessage = `⚠️ Server error (${status}). Please try again.`;
        debugInfo = data?.detail || error.response.statusText || 'Unknown server error';
    }
  } else if (error.request) {
    // Network error - request was made but no response received
    if (error.code === 'ECONNABORTED' || error.message.includes('timeout')) {
      userMessage = '⏱️ Request timeout. The server is taking too long to respond. Please try again.';
      debugInfo = 'Request timeout - server took too long to respond';
    } else if (error.code === 'ERR_NETWORK' || error.message.includes('Network Error')) {
      userMessage = '🌐 Network error. Please check your internet connection and try again.';
      debugInfo = 'Network connectivity issue - unable to reach server';
    } else {
      userMessage = '🔌 Unable to connect to the server. Please check your connection and try again.';
      debugInfo = `Network error: ${error.message}`;
    }
  } else {
    // Something else happened
    userMessage = '❓ An unexpected error occurred. Please refresh the page and try again.';
    debugInfo = error.message || 'Unknown error during request setup';
  }

  // Create enhanced error object
  const enhancedError = new Error(userMessage);
  (enhancedError as any).originalError = error;
  (enhancedError as any).debugInfo = debugInfo;
  (enhancedError as any).status = error.response?.status;
  (enhancedError as any).isAuthError = error.response?.status === 401;
  (enhancedError as any).isNetworkError = !error.response;
  
  console.error('🔍 Enhanced Error Info:', {
    userMessage,
    debugInfo,
    status: error.response?.status,
    isAuthError: error.response?.status === 401,
    isNetworkError: !error.response,
    originalError: error
  });

  throw enhancedError;
};

// Safe API call wrapper with timeout and cancellation
export async function safeApiCall<T>(
  apiCall: () => Promise<T>,
  options?: {
    timeout?: number;
    signal?: AbortSignal;
  }
): Promise<T> {
  const { timeout = 30000, signal } = options || {};
  
  const timeoutPromise = new Promise<never>((_, reject) => {
    setTimeout(() => reject(new Error('Request timeout')), timeout);
  });

  try {
    const result = await Promise.race([apiCall(), timeoutPromise]);
    return result;
  } catch (error) {
    if (signal?.aborted) {
      throw new Error('Request cancelled');
    }
    
    if (axios.isAxiosError(error)) {
      handleApiError(error);
    }
    
    throw error;
  }
}

// Export the API URL (apiClient is already exported above)
export { API_URL }; 
 