import { useCallback, useEffect, useRef, useState } from 'react';

/**
 * Custom hook that provides a safe version of setState that checks if component is mounted
 * Prevents memory leaks from setState calls after component unmount
 */
export function useSafeState<T>(initialState: T | (() => T)) {
  const [state, setState] = useState(initialState);
  const isMountedRef = useRef(true);

  useEffect(() => {
    return () => {
      isMountedRef.current = false;
    };
  }, []);

  const setSafeState = useCallback((newState: T | ((prevState: T) => T)) => {
    if (isMountedRef.current) {
      setState(newState);
    }
  }, []);

  return [state, setSafeState] as const;
}

/**
 * Custom hook for safe async operations that prevents memory leaks
 */
export function useSafeAsync<T>() {
  const isMountedRef = useRef(true);
  const [loading, setLoading] = useSafeState(false);
  const [error, setError] = useSafeState<Error | null>(null);
  const [data, setData] = useSafeState<T | null>(null);

  useEffect(() => {
    return () => {
      isMountedRef.current = false;
    };
  }, []);

  const execute = useCallback(async (asyncFunction: () => Promise<T>) => {
    setLoading(true);
    setError(null);
    
    try {
      const result = await asyncFunction();
      if (isMountedRef.current) {
        setData(result);
        setLoading(false);
        return result;
      }
    } catch (err) {
      if (isMountedRef.current) {
        setError(err as Error);
        setLoading(false);
        throw err;
      }
    }
  }, [setData, setError, setLoading]);

  return { execute, loading, error, data };
} 