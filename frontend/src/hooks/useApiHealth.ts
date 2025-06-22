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
      // Set the error message that will be displayed
      setApiGlobalError('Could not connect to the backend API. Please ensure the server is running and accessible.');
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