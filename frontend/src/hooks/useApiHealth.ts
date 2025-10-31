import { useState, useCallback } from 'react';
import { checkApiHealth } from '../services/api';
import { logger } from '../utils/logger';

export interface UseApiHealthReturn {
  apiGlobalError: string | null;
  setApiGlobalError: React.Dispatch<React.SetStateAction<string | null>>;
  checkApiConnection: () => Promise<void>; // Function to manually re-trigger health check
  clearApiGlobalError: () => void;
}

export const useApiHealth = (): UseApiHealthReturn => {
  const [apiGlobalError, setApiGlobalError] = useState<string | null>(null);

  const checkApiConnection = useCallback(async () => {
    try {
      await checkApiHealth();
      setApiGlobalError(null);
      logger.log("API health check successful from useApiHealth.");
    } catch (error) {
      logger.error('API health check failed in useApiHealth:', error);
      
      // Be more specific about when to show the connection error
      // Don't show connection errors for authentication issues (401, 403)
      const isAuthError = error?.response?.status === 401 || error?.response?.status === 403;
      const isServerError = error?.response?.status >= 500;
      const isNetworkError = !error?.response || error?.code === 'ECONNREFUSED' || error?.message?.includes('Network Error');
      
      if (isAuthError) {
        // Don't show global error for auth issues - these are handled by individual components
        logger.warn('Health check failed due to authentication - this is normal and will be handled by auth components');
        setApiGlobalError(null);
      } else if (isNetworkError || isServerError) {
        // Only show connection error for actual network/server issues
        setApiGlobalError('Could not connect to the backend API. Please ensure the server is running and accessible.');
      } else {
        // Other HTTP errors (400, 404, etc.) - show a generic message
        setApiGlobalError(`API request failed with status ${error?.response?.status || 'unknown'}. Please try again.`);
      }
    }
  }, [setApiGlobalError]);

  const clearApiGlobalError = useCallback(() => {
    setApiGlobalError(null);
  }, [setApiGlobalError]);

  return {
    apiGlobalError,
    setApiGlobalError,
    checkApiConnection,
    clearApiGlobalError
  };
}; 