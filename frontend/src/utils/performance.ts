import React from 'react';

/**
 * Performance Utilities for Owen AI Frontend
 * Optimized hooks and utilities for better user experience
 */

// Debounce utility function
export function debounce<T extends (...args: any[]) => any>(
  func: T,
  wait: number
): (...args: Parameters<T>) => void {
  let timeoutId: ReturnType<typeof setTimeout> | null = null;
  
  return (...args: Parameters<T>) => {
    if (timeoutId !== null) {
      clearTimeout(timeoutId);
    }
    timeoutId = setTimeout(() => func(...args), wait);
  };
}

// Throttle utility function  
export function throttle<T extends (...args: any[]) => any>(
  func: T,
  limit: number
): (...args: Parameters<T>) => void {
  let inThrottle: boolean;
  let timeoutId: ReturnType<typeof setTimeout> | null = null;
  
  return (...args: Parameters<T>) => {
    if (!inThrottle) {
      func(...args);
      inThrottle = true;
      timeoutId = setTimeout(() => {
        inThrottle = false;
      }, limit);
    }
  };
}

// Memoization utility
export function memoize<T extends (...args: any[]) => any>(
  fn: T,
  maxCacheSize: number = 100
): T {
  const cache = new Map<string, ReturnType<T>>();
  
  return ((...args: Parameters<T>): ReturnType<T> => {
    const key = JSON.stringify(args);
    
    if (cache.has(key)) {
      return cache.get(key)!;
    }
    
    if (cache.size >= maxCacheSize) {
      const firstKey = cache.keys().next().value;
      cache.delete(firstKey);
    }
    
    const result = fn(...args);
    cache.set(key, result);
    return result;
  }) as T;
}

// Performance monitoring
export class PerformanceMonitor {
  private static measurements: Map<string, number> = new Map();
  
  static start(label: string): void {
    this.measurements.set(label, performance.now());
  }
  
  static end(label: string): number {
    const startTime = this.measurements.get(label);
    if (!startTime) {
      console.warn(`Performance measurement '${label}' was not started`);
      return 0;
    }
    
    const duration = performance.now() - startTime;
    this.measurements.delete(label);
    
    console.log(`Performance [${label}]: ${duration.toFixed(2)}ms`);
    return duration;
  }
  
  static measure<T>(label: string, fn: () => T): T {
    this.start(label);
    try {
      return fn();
    } finally {
      this.end(label);
    }
  }
}

// Memory usage monitoring (simplified for browser compatibility)
export function getMemoryUsage(): { usedJSHeapSize?: number } | null {
  if ('memory' in performance) {
    return (performance as any).memory;
  }
  return null;
}

// Intersection Observer for lazy loading
export function createIntersectionObserver(
  callback: (entries: IntersectionObserverEntry[]) => void,
  options?: IntersectionObserverInit
): IntersectionObserver | null {
  if ('IntersectionObserver' in window) {
    return new IntersectionObserver(callback, {
      rootMargin: '50px',
      threshold: 0.1,
      ...options
    });
  }
  return null;
}

// Request Animation Frame utility
export function nextFrame(callback: () => void): number {
  return requestAnimationFrame(callback);
}

// Batch DOM updates
export function batchDOMUpdates(updates: (() => void)[]): void {
  nextFrame(() => {
    updates.forEach(update => update());
  });
}

// Web Workers utility (simplified)
export function createWorkerTask<T>(
  workerScript: string,
  data: any
): Promise<T> {
  return new Promise((resolve, reject) => {
    if ('Worker' in window) {
      const worker = new Worker(workerScript);
      worker.postMessage(data);
      
      worker.onmessage = (event) => {
        resolve(event.data);
        worker.terminate();
      };
      
      worker.onerror = (error) => {
        reject(error);
        worker.terminate();
      };
    } else {
      reject(new Error('Web Workers not supported'));
    }
  });
}

// Lazy component loading
export function createLazyComponent(
  importFn: () => Promise<{ default: React.ComponentType<any> }>
): React.LazyExoticComponent<React.ComponentType<any>> {
  return React.lazy(() =>
    importFn().catch(() => ({
      default: () => React.createElement('div', {}, 'Failed to load component')
    }))
  );
}

// Simple cache implementation
export class SimpleCache<T> {
  private cache = new Map<string, { value: T; timestamp: number }>();
  private ttl: number;
  
  constructor(ttlMs: number = 300000) { // 5 minutes default
    this.ttl = ttlMs;
  }
  
  set(key: string, value: T): void {
    this.cache.set(key, {
      value,
      timestamp: Date.now()
    });
  }
  
  get(key: string): T | null {
    const item = this.cache.get(key);
    if (!item) return null;
    
    if (Date.now() - item.timestamp > this.ttl) {
      this.cache.delete(key);
      return null;
    }
    
    return item.value;
  }
  
  clear(): void {
    this.cache.clear();
  }
}

// Request Animation Frame debouncer for smooth animations
export function rafDebounce<T extends (...args: any[]) => any>(
  func: T
): (...args: Parameters<T>) => void {
  let rafId: number | null = null;
  
  return (...args: Parameters<T>) => {
    if (rafId) {
      cancelAnimationFrame(rafId);
    }
    
    rafId = requestAnimationFrame(() => {
      func(...args);
      rafId = null;
    });
  };
}

// Detect performance issues
export function detectPerformanceIssues(): string[] {
  const issues: string[] = [];
  
  // Check memory usage
  const memory = getMemoryUsage();
  if (memory) {
    const usedRatio = memory.usedJSHeapSize / memory.totalJSHeapSize;
    if (usedRatio > 0.9) {
      issues.push('High memory usage detected');
    }
  }
  
  // Check if main thread is blocked
  const start = performance.now();
  let iterations = 0;
  while (performance.now() - start < 5) {
    iterations++;
  }
  
  if (iterations < 100000) {
    issues.push('Main thread appears to be blocked');
  }
  
  return issues;
}

// Efficient deep comparison for React dependencies
export function shallowEqual(obj1: any, obj2: any): boolean {
  if (obj1 === obj2) return true;
  if (!obj1 || !obj2) return false;
  
  const keys1 = Object.keys(obj1);
  const keys2 = Object.keys(obj2);
  
  if (keys1.length !== keys2.length) return false;
  
  for (const key of keys1) {
    if (obj1[key] !== obj2[key]) return false;
  }
  
  return true;
}

export const perfMonitor = PerformanceMonitor.getInstance(); 