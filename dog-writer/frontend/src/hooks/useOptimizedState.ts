/**
 * Optimized State Management Hook
 * 
 * Provides performance-optimized state management with:
 * - Automatic memoization
 * - Debounced updates
 * - Batch updates
 * - Memory leak prevention
 */

import { useCallback, useRef, useEffect, useMemo } from 'react';
import { debounce } from '../utils/performance';
import { logger } from '../utils/logger';

interface UseOptimizedStateOptions<T> {
  debounceMs?: number;
  enableMemoization?: boolean;
  onStateChange?: (newState: T, prevState: T) => void;
  validator?: (state: T) => boolean;
}

export function useOptimizedState<T>(
  initialState: T,
  options: UseOptimizedStateOptions<T> = {}
) {
  const {
    debounceMs = 300,
    enableMemoization = true,
    onStateChange,
    validator
  } = options;

  const stateRef = useRef<T>(initialState);
  const previousStateRef = useRef<T>(initialState);
  const listenersRef = useRef<Set<(state: T) => void>>(new Set());
  const mountedRef = useRef(true);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      mountedRef.current = false;
      listenersRef.current.clear();
    };
  }, []);

  // Debounced state update
  const debouncedUpdate = useMemo(
    () => debounce((newState: T) => {
      if (!mountedRef.current) return;

      // Validate state if validator provided
      if (validator && !validator(newState)) {
        logger.warn('State validation failed, update rejected');
        return;
      }

      const prevState = stateRef.current;
      stateRef.current = newState;

      // Call change handler
      if (onStateChange) {
        onStateChange(newState, prevState);
      }

      // Notify listeners
      listenersRef.current.forEach(listener => {
        try {
          listener(newState);
        } catch (error) {
          logger.error('Error in state listener:', error);
        }
      });

      previousStateRef.current = prevState;
    }, debounceMs),
    [debounceMs, onStateChange, validator]
  );

  // Optimized setter
  const setState = useCallback((newState: T | ((prev: T) => T)) => {
    const updatedState = typeof newState === 'function' 
      ? (newState as (prev: T) => T)(stateRef.current)
      : newState;

    // Skip if state hasn't changed (shallow comparison)
    if (enableMemoization && updatedState === stateRef.current) {
      return;
    }

    debouncedUpdate(updatedState);
  }, [debouncedUpdate, enableMemoization]);

  // Subscribe to state changes
  const subscribe = useCallback((listener: (state: T) => void) => {
    listenersRef.current.add(listener);
    
    // Return unsubscribe function
    return () => {
      listenersRef.current.delete(listener);
    };
  }, []);

  // Get current state (memoized)
  const getState = useCallback(() => stateRef.current, []);

  // Batch multiple updates
  const batchUpdate = useCallback((updates: Partial<T>) => {
    const currentState = stateRef.current;
    const newState = { ...currentState, ...updates };
    setState(newState);
  }, [setState]);

  return {
    state: stateRef.current,
    setState,
    getState,
    subscribe,
    batchUpdate,
    previousState: previousStateRef.current
  };
} 