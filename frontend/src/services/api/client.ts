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
  console.error('🔄 === RETRY REQUEST FUNCTION CALLED ===');
  console.error('🔄 Original error details:', {
    url: error.config?.url,
    status: error.response?.status,
    message: error.message,
    hasResponse: !!error.response,
    hasRequest: !!error.request
  });

  const config = error.config as AxiosRequestConfig & { _retry?: number };
  
  console.error('🔄 Retry config check:', {
    hasConfig: !!config,
    retryConditionResult: config ? retryConfig.retryCondition(error) : false,
    currentRetryCount: config?._retry || 0,
    maxRetries: retryConfig.retries
  });
  
  if (!config || !retryConfig.retryCondition(error)) {
    console.error('🔄 ❌ Retry condition failed - rejecting error');
    return Promise.reject(error);
  }

  config._retry = config._retry || 0;

  if (config._retry >= retryConfig.retries) {
    console.error('🔄 ❌ Max retries reached - rejecting error');
    return Promise.reject(error);
  }

  config._retry += 1;
  
  console.error(`🔄 ✅ Proceeding with retry attempt ${config._retry}/${retryConfig.retries}`);

  if (retryConfig.onRetry) {
    console.error('🔄 Calling onRetry callback...');
    retryConfig.onRetry(error, config._retry);
  }

  const delay = retryConfig.retryDelay(config._retry);
  console.error(`🔄 Waiting ${delay}ms before retry...`);
  await new Promise(resolve => setTimeout(resolve, delay));

  console.error('🔄 🚀 Making retry request with config:', {
    url: config.url,
    method: config.method,
    hasAuthHeader: !!config.headers?.Authorization,
    authHeaderPreview: config.headers?.Authorization?.substring(0, 20) + '...',
    retryCount: config._retry
  });

  // CRITICAL: This is where the retry request is made
  try {
    const retryResponse = await apiClient(config);
    console.error('🔄 ✅ Retry request succeeded:', {
      status: retryResponse.status,
      url: retryResponse.config.url
    });
    return retryResponse;
  } catch (retryError) {
    console.error('🔄 ❌ Retry request failed:', {
      message: (retryError as any).message,
      status: (retryError as any).response?.status,
      hasResponse: !!(retryError as any).response,
      hasRequest: !!(retryError as any).request
    });
    throw retryError;
  }
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

    // ENHANCED DEBUGGING: Log every detail about the error
    console.error('🚨 === RESPONSE INTERCEPTOR ERROR ANALYSIS ===');
    console.error(`❌ API Error: ${error.config?.url} - Status: ${error.response?.status || 'undefined'}`);
    console.error('❌ Full Error Details:', {
      message: error.message,
      code: error.code,
      status: error.response?.status,
      statusText: error.response?.statusText,
      data: error.response?.data,
      hasResponse: !!error.response,
      hasRequest: !!error.request,
      isAxiosError: error.isAxiosError,
      config: {
        url: error.config?.url,
        method: error.config?.method,
        headers: error.config?.headers,
        timeout: error.config?.timeout
      }
    });

    // ENHANCED DEBUGGING: Check if this is a retry
    if (originalRequest._retry) {
      console.error('🔄 THIS IS A RETRY ATTEMPT - Original request already failed');
      console.error('🔍 Retry context:', {
        retryCount: originalRequest._retry,
        originalUrl: originalRequest.url,
        originalMethod: originalRequest.method
      });
    } else {
      console.error('🆕 THIS IS THE FIRST ATTEMPT');
    }

    // CRITICAL FIX: Handle 401 errors IMMEDIATELY - do NOT proceed to retry logic
    if (error.response?.status === 401) {
      console.error('🔐 === 401 ERROR DETECTED ===');
      console.error('🔐 Processing 401 immediately, NO RETRY');
      console.error('🔐 Error response data:', error.response.data);
      
      // Clear tokens immediately
      clearAuthTokens();
      
      // Dispatch auth event
      console.log('📢 Dispatching auth:token-expired event...');
      window.dispatchEvent(new CustomEvent('auth:token-expired', {
        detail: { 
          reason: 'Authentication failed', 
          status: 401,
          originalError: error
        }
      }));
      
      // Process the error through handleApiError and throw immediately
      console.error('🔐 Calling handleApiError for 401...');
      handleApiError(error);
      // handleApiError throws, so this line will never be reached
    }

    // CRITICAL FIX: Handle other 4xx client errors immediately - do NOT retry
    if (error.response?.status && error.response.status >= 400 && error.response.status < 500) {
      console.error(`🚫 === ${error.response.status} CLIENT ERROR DETECTED ===`);
      console.error(`🚫 Processing ${error.response.status} immediately, NO RETRY`);
      console.error('🚫 Error response data:', error.response.data);
      handleApiError(error);
      // handleApiError throws, so this line will never be reached
    }

    // ENHANCED DEBUGGING: Log retry decision logic
    console.error('🤔 === RETRY DECISION ANALYSIS ===');
    console.error('🤔 Checking if retry should happen...');
    console.error('🤔 originalRequest._retry:', originalRequest._retry);
    console.error('🤔 error.response exists:', !!error.response);
    console.error('🤔 error.response.status:', error.response?.status);
    
    // RETRY LOGIC: Only for 5xx server errors and actual network errors (no response)
    if (!originalRequest._retry) {
      // Only retry for server errors (5xx) or actual network errors (no response)
      const shouldRetry = !error.response || (error.response.status >= 500);
      
      console.error('🤔 shouldRetry calculation:', {
        noResponse: !error.response,
        isServerError: error.response?.status >= 500,
        finalDecision: shouldRetry
      });
      
      if (shouldRetry) {
        console.error(`🔄 === RETRY LOGIC ACTIVATED ===`);
        console.error(`🔄 Attempting retry for ${error.response?.status || 'network'} error...`);
        console.error('🔄 About to call retryRequest...');
        return retryRequest(error);
      } else {
        console.error(`❌ === NO RETRY DECISION ===`);
        console.error(`❌ No retry for ${error.response?.status} error - handling immediately`);
        handleApiError(error);
        // handleApiError throws, so this line will never be reached
      }
    }

    // If we've already retried, process the error
    console.error('❌ === MAX RETRIES REACHED ===');
    console.error('❌ Max retries reached, processing error:', {
      status: error.response?.status,
      message: error.message,
      isRetry: !!originalRequest._retry
    });
    
    handleApiError(error);
    // handleApiError throws, so this line will never be reached
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
 