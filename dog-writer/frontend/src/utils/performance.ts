/**
 * Performance Utilities
 * 
 * Collection of utilities for optimizing frontend performance:
 * - Debouncing and throttling
 * - Memoization
 * - Lazy loading
 * - Bundle splitting helpers
 */

// Debounce function for delayed execution
export function debounce<T extends (...args: any[]) => any>(
  func: T,
  waitMs: number
): (...args: Parameters<T>) => void {
  let timeoutId: NodeJS.Timeout | null = null;
  
  return (...args: Parameters<T>) => {
    if (timeoutId) {
      clearTimeout(timeoutId);
    }
    
    timeoutId = setTimeout(() => {
      func(...args);
      timeoutId = null;
    }, waitMs);
  };
}

// Throttle function for rate limiting
export function throttle<T extends (...args: any[]) => any>(
  func: T,
  limitMs: number
): (...args: Parameters<T>) => void {
  let lastCall = 0;
  let timeoutId: NodeJS.Timeout | null = null;
  
  return (...args: Parameters<T>) => {
    const now = Date.now();
    
    if (now - lastCall >= limitMs) {
      lastCall = now;
      func(...args);
    } else if (!timeoutId) {
      timeoutId = setTimeout(() => {
        lastCall = Date.now();
        func(...args);
        timeoutId = null;
      }, limitMs - (now - lastCall));
    }
  };
}

// Simple memoization for expensive calculations
export function memoize<T extends (...args: any[]) => any>(
  func: T,
  maxCacheSize: number = 100
): T {
  const cache = new Map();
  const keyOrder: string[] = [];
  
  return ((...args: Parameters<T>) => {
    const key = JSON.stringify(args);
    
    if (cache.has(key)) {
      return cache.get(key);
    }
    
    const result = func(...args);
    
    // Implement LRU cache
    if (cache.size >= maxCacheSize) {
      const oldestKey = keyOrder.shift();
      if (oldestKey) {
        cache.delete(oldestKey);
      }
    }
    
    cache.set(key, result);
    keyOrder.push(key);
    
    return result;
  }) as T;
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

// Intersection Observer for lazy loading
export function createIntersectionObserver(
  callback: (entries: IntersectionObserverEntry[]) => void,
  options: IntersectionObserverInit = {}
): IntersectionObserver {
  const defaultOptions: IntersectionObserverInit = {
    root: null,
    rootMargin: '50px',
    threshold: 0.1,
    ...options
  };
  
  return new IntersectionObserver(callback, defaultOptions);
}

// Performance monitoring
export class PerformanceMonitor {
  private static instance: PerformanceMonitor;
  private metrics: Map<string, number[]> = new Map();
  
  static getInstance(): PerformanceMonitor {
    if (!PerformanceMonitor.instance) {
      PerformanceMonitor.instance = new PerformanceMonitor();
    }
    return PerformanceMonitor.instance;
  }
  
  measure<T>(name: string, func: () => T): T {
    const start = performance.now();
    const result = func();
    const end = performance.now();
    const duration = end - start;
    
    if (!this.metrics.has(name)) {
      this.metrics.set(name, []);
    }
    
    const measurements = this.metrics.get(name)!;
    measurements.push(duration);
    
    // Keep only last 100 measurements
    if (measurements.length > 100) {
      measurements.shift();
    }
    
    return result;
  }
  
  async measureAsync<T>(name: string, func: () => Promise<T>): Promise<T> {
    const start = performance.now();
    const result = await func();
    const end = performance.now();
    const duration = end - start;
    
    if (!this.metrics.has(name)) {
      this.metrics.set(name, []);
    }
    
    const measurements = this.metrics.get(name)!;
    measurements.push(duration);
    
    if (measurements.length > 100) {
      measurements.shift();
    }
    
    return result;
  }
  
  getStats(name: string) {
    const measurements = this.metrics.get(name) || [];
    if (measurements.length === 0) {
      return null;
    }
    
    const avg = measurements.reduce((a, b) => a + b, 0) / measurements.length;
    const min = Math.min(...measurements);
    const max = Math.max(...measurements);
    
    return { avg, min, max, count: measurements.length };
  }
  
  getAllStats() {
    const stats: Record<string, any> = {};
    for (const [name] of this.metrics) {
      stats[name] = this.getStats(name);
    }
    return stats;
  }
}

// Bundle splitting helpers
export const loadComponent = (importFunc: () => Promise<any>) => {
  return React.lazy(() =>
    importFunc().catch((error) => {
      console.error('Failed to load component:', error);
      // Return a fallback component
      return {
        default: () => React.createElement('div', {}, 'Failed to load component')
      };
    })
  );
};

// Memory usage monitoring
export function getMemoryUsage(): MemoryInfo | null {
  if ('memory' in performance) {
    return (performance as any).memory;
  }
  return null;
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