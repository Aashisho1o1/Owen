/**
 * API Client Configuration
 * Centralized HTTP client setup with authentication and error handling.
 */

import axios, { AxiosResponse } from 'axios';
import { getStoredTokens, clearAuthTokens } from './auth';
import { logger } from '../../utils/logger';

// Normalize API_URL to prevent double slashes (trailing slash issues)
const API_URL = import.meta.env.VITE_API_URL?.replace(/\/+$/, '') || '';

if (!API_URL) {
  throw new Error('VITE_API_URL environment variable is required but not defined');
}

logger.info('API configured', { API_URL, env_loaded: !!import.meta.env.VITE_API_URL });

if (import.meta.env.DEV && import.meta.env.VITE_API_URL?.endsWith('/')) {
  logger.warn('VITE_API_URL ends with trailing slash — auto-corrected. Remove it from your .env file.');
}

// Create axios instance with configuration
const apiClient = axios.create({
  baseURL: API_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Special timeout for voice analysis (Gemini 2.5 Flash can be slow for complex analysis)
const VOICE_ANALYSIS_TIMEOUT = 300000; // 5 minutes

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

export const updateApiClientToken = (token: string | null, tokenType: string = 'Bearer') => {
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
    logger.info('Refreshing tokens');

    // Use a fresh axios instance to avoid interceptor loops
    const response = await axios.post(`${API_URL}/api/auth/refresh`, {
      refresh_token: storedRefreshToken
    }, {
      headers: { 'Content-Type': 'application/json' }
    });

    const { access_token, refresh_token: newRefreshToken, token_type, expires_in } = response.data;

    // Store new tokens
    localStorage.setItem('owen_access_token', access_token);
    localStorage.setItem('owen_refresh_token', newRefreshToken);
    localStorage.setItem('owen_token_type', token_type);
    localStorage.setItem('owen_token_expires', (Date.now() + expires_in * 1000).toString());

    updateApiClientToken(access_token, token_type);

    return access_token;
  } catch (error) {
    logger.error('Token refresh failed', error);
    clearAuthTokens();
    updateApiClientToken(null);
    throw error;
  }
};

// Request interceptor
apiClient.interceptors.request.use(
  (config) => {
    logger.log(`API Request: ${config.method?.toUpperCase()} ${config.url}`);

    // Development safety check for double slashes in URLs
    if (import.meta.env.DEV && config.url?.includes('//api/')) {
      logger.error('Double slash detected in API URL — check VITE_API_URL trailing slash', config.url);
    }

    // Extended timeout for voice analysis endpoints
    if (config.url?.includes('/character-voice/analyze')) {
      logger.info('Voice analysis request: using extended timeout (5 min)');
      config.timeout = VOICE_ANALYSIS_TIMEOUT;
      config.headers = {
        ...config.headers,
        'X-Fresh-Request': Date.now().toString()
      };
    }

    const storedTokens = getStoredTokens();
    if (storedTokens.accessToken) {
      config.headers.Authorization = `Bearer ${storedTokens.accessToken}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Single response interceptor: error logging + token refresh on 401/403
apiClient.interceptors.response.use(
  (response: AxiosResponse) => response,
  async (error) => {
    const originalRequest = error.config;

    // Handle 401 AND 403 errors with token refresh
    if ((error.response?.status === 401 || error.response?.status === 403) && !originalRequest._retry) {
      const storedTokens = getStoredTokens();

      // No token = user hasn't authenticated yet, don't trigger logout
      if (!storedTokens.accessToken) {
        return Promise.reject(error);
      }

      // Guest sessions have access tokens but no refresh tokens
      if (!storedTokens.refreshToken) {
        return Promise.reject(error);
      }

      // Don't attempt token refresh for auth endpoints to prevent infinite loops
      const isAuthEndpoint = originalRequest.url && (
        originalRequest.url.includes('/api/auth/login') ||
        originalRequest.url.includes('/api/auth/register') ||
        originalRequest.url.includes('/api/auth/refresh')
      );

      if (isAuthEndpoint) {
        return Promise.reject(error);
      }

      if (isRefreshing) {
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
        const newToken = await refreshTokens();

        processQueue(null, newToken);
        isRefreshing = false;

        originalRequest.headers.Authorization = `Bearer ${newToken}`;
        return apiClient(originalRequest);

      } catch (refreshError) {
        logger.error('Token refresh failed — logging out user');

        processQueue(refreshError, null);
        isRefreshing = false;

        clearAuthTokens();
        updateApiClientToken(null);

        // Dispatch token expired event ONLY once
        window.dispatchEvent(new CustomEvent('auth:token-expired'));

        throw new Error('Authentication required. Please sign in again to continue using the AI Writing Assistant.');
      }
    }

    // Log and handle other HTTP errors
    if (error.response) {
      logger.error(`API Error ${error.response.status}: ${error.config?.method?.toUpperCase()} ${error.config?.url}`);
      throw error;
    } else if (error.request) {
      logger.error('Network error', error.message);
      throw new Error('Network error. Please check your connection and try again.');
    } else {
      logger.error('Request error', error.message);
      throw error;
    }
  }
);

export default apiClient;
