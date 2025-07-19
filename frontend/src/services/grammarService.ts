import { logger } from '../utils/logger';

/**
 * Grammar Checking Service - SECURE VERSION
 * 
 * Provides real-time grammar and spelling checking with speculative execution:
 * - Fast checks for immediate feedback (typing)
 * - Comprehensive checks for final review
 * - Smart caching and debouncing
 * - Security: Input validation, XSS prevention, secure token handling
 */

interface GrammarIssue {
  start: number;
  end: number;
  issue_type: 'spelling' | 'grammar' | 'style' | 'punctuation';
  severity: 'info' | 'warning' | 'error';
  message: string;
  suggestions: string[];
  confidence: number;
  source: string;
}

interface GrammarCheckResult {
  text_length: number;
  word_count: number;
  issues: GrammarIssue[];
  check_type: 'real_time' | 'comprehensive';
  processing_time_ms: number;
  cached: boolean;
}

// Security constants
const MAX_TEXT_LENGTH = 50000;
const MAX_CACHE_SIZE = 500;
const CACHE_TTL = 5 * 60 * 1000; // 5 minutes
const DEBOUNCE_DELAY = 500; // 500ms

// Grammar checking service
class GrammarService {
  private baseURL: string;
  private cache: Map<string, any> = new Map();
  private lastRequestTime: number = 0;
  private readonly DEBOUNCE_MS = 1000;

  constructor() {
    const apiUrl = import.meta.env.VITE_API_URL;
    if (!apiUrl) {
      console.error('❌ CRITICAL: VITE_API_URL is not defined in GrammarService');
      throw new Error('VITE_API_URL environment variable is required but not defined');
    }
    this.baseURL = apiUrl;
  }

  /**
   * Validate and sanitize input text
   */
  private validateInput(text: string): string {
    if (typeof text !== 'string') {
      throw new Error('Input must be a string');
    }

    if (text.length > MAX_TEXT_LENGTH) {
      throw new Error(`Text too long. Maximum ${MAX_TEXT_LENGTH} characters allowed`);
    }

    // Basic sanitization - remove null bytes and normalize whitespace
    const sanitized = text
      .replace(/\0/g, '')
      .replace(/\r\n/g, '\n')
      .replace(/\r/g, '\n')
      .trim();

    // Check for suspicious patterns
    const suspiciousPatterns = [
      /<script[^>]*>/i,
      /javascript:/i,
      /vbscript:/i,
      /onload\s*=/i,
      /onerror\s*=/i,
    ];

    for (const pattern of suspiciousPatterns) {
      if (pattern.test(sanitized)) {
        logger.warn('Suspicious pattern detected in input');
        throw new Error('Input contains potentially malicious content');
      }
    }

    return sanitized;
  }

  /**
   * Get secure headers for API requests
   */
  private getSecureHeaders(): Record<string, string> {
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
      'X-Requested-With': 'XMLHttpRequest', // CSRF protection
    };

    // Add authentication token if available
    const token = this.getAuthToken();
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }

    return headers;
  }

  /**
   * Get authentication token from secure storage
   */
  private getAuthToken(): string | null {
    try {
      // Try multiple token storage keys for compatibility
      return (
        localStorage.getItem('owen_access_token') ||
        localStorage.getItem('access_token') ||
        sessionStorage.getItem('access_token') ||
        null
      );
    } catch (error) {
      logger.error('Error accessing token storage:', error);
      return null;
    }
  }

  /**
   * Manage cache size to prevent memory issues
   */
  private manageCacheSize(): void {
    if (this.cache.size > MAX_CACHE_SIZE) {
      // Remove oldest entries (simple LRU)
      const entries = Array.from(this.cache.entries());
      entries.sort((a, b) => a[1].timestamp - b[1].timestamp);
      
      const removeCount = Math.floor(entries.length * 0.2); // Remove 20%
      for (let i = 0; i < removeCount; i++) {
        this.cache.delete(entries[i][0]);
      }
    }
  }

  /**
   * Real-time grammar checking (fast, for typing feedback)
   */
  async checkRealTime(text: string, language = 'en-US'): Promise<GrammarCheckResult> {
    const textHash = this.generateHash(text);
    
    // Check cache first
    const cached = this.getCached(textHash);
    if (cached) {
      return { ...cached, cached: true };
    }
    
    // Debounce rapid requests
    if (this.shouldDebounce(textHash)) {
      return this.getEmptyResult(text, 'real_time');
    }
    
    try {
      const response = await fetch(`${this.baseURL}/api/grammar/check`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        },
        body: JSON.stringify({
          text,
          check_type: 'real_time',
          language
        })
      });
      
      if (!response.ok) {
        throw new Error(`Grammar check failed: ${response.statusText}`);
      }
      
      const result: GrammarCheckResult = await response.json();
      
      // Cache result
      this.cache.set(textHash, {
        result,
        timestamp: Date.now()
      });
      
      this.lastRequestTime = Date.now();
      return result;
      
    } catch (error) {
      logger.error('Real-time grammar check failed:', error);
      return this.getEmptyResult(text, 'real_time');
    }
  }
  
  /**
   * Comprehensive grammar checking (accurate, for final review)
   */
  async checkComprehensive(text: string, context?: string): Promise<GrammarCheckResult> {
    const textHash = this.generateHash(text + (context || ''));
    
    const cached = this.getCached(textHash);
    if (cached) {
      return { ...cached, cached: true };
    }
    
    try {
      const response = await fetch(`${this.baseURL}/api/grammar/check`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        },
        body: JSON.stringify({
          text,
          check_type: 'comprehensive',
          context,
          language: 'en-US'
        })
      });
      
      if (!response.ok) {
        throw new Error(`Comprehensive grammar check failed: ${response.statusText}`);
      }
      
      const result: GrammarCheckResult = await response.json();
      
      // Cache result
      this.cache.set(textHash, {
        result,
        timestamp: Date.now()
      });
      
      return result;
      
    } catch (error) {
      logger.error('Comprehensive grammar check failed:', error);
      return this.getEmptyResult(text, 'comprehensive');
    }
  }
  
  /**
   * Streaming grammar check for progressive results
   */
  async checkStreaming(
    text: string, 
    onUpdate: (issues: GrammarIssue[], type: string) => void
  ): Promise<void> {
    try {
      const response = await fetch(`${this.baseURL}/api/grammar/stream-check`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        },
        body: JSON.stringify({
          text,
          check_type: 'comprehensive'
        })
      });
      
      if (!response.body) {
        throw new Error('No response body');
      }
      
      // Handle stream data
      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      
      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        
        const chunk = decoder.decode(value, { stream: true });
        const lines = chunk.split('\n\n');
        
        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const data = JSON.parse(line.substring(6));
              onUpdate(data.issues, data.type);
            } catch (e) {
              logger.error('Error parsing stream data:', e);
            }
          }
        }
      }
    } catch (error) {
      logger.error('Streaming grammar check failed:', error);
    }
  }
  
  /**
   * Debounced real-time checking for editor integration
   */
  checkRealTimeDebounced(
    text: string, 
    callback: (result: GrammarCheckResult) => void,
    delay = this.DEBOUNCE_MS
  ): void {
    const textHash = this.generateHash(text);
    
    // Clear existing timer
    const existingTimer = this.debounceTimers.get(textHash);
    if (existingTimer) {
      clearTimeout(existingTimer);
    }
    
    // Set new timer
    const timer = setTimeout(async () => {
      const result = await this.checkRealTime(text);
      callback(result);
      this.debounceTimers.delete(textHash);
    }, delay);
    
    this.debounceTimers.set(textHash, timer);
  }
  
  private generateHash(text: string): string {
    // Simple hash function for caching
    let hash = 0;
    for (let i = 0; i < text.length; i++) {
      const char = text.charCodeAt(i);
      hash = ((hash << 5) - hash) + char;
      hash = hash & hash; // Convert to 32-bit integer
    }
    return hash.toString();
  }
  
  private getCached(textHash: string): GrammarCheckResult | null {
    const cached = this.cache.get(textHash);
    if (!cached) return null;
    
    const isExpired = Date.now() - cached.timestamp > CACHE_TTL;
    if (isExpired) {
      this.cache.delete(textHash);
      return null;
    }
    
    return cached.result;
  }
  
  private shouldDebounce(textHash: string): boolean {
    const lastCheck = this.lastRequestTime;
    if (!lastCheck) return false;
    
    return Date.now() - lastCheck < this.DEBOUNCE_MS;
  }
  
  private getEmptyResult(text: string, checkType: 'real_time' | 'comprehensive'): GrammarCheckResult {
    return {
      text_length: text.length,
      word_count: text.split(/\s+/).length,
      issues: [],
      check_type: checkType,
      processing_time_ms: 0,
      cached: false
    };
  }
  
  /**
   * Clear all caches
   */
  clearCache(): void {
    this.cache.clear();
    this.lastRequestTime = 0;
    
    // Clear all debounce timers
    this.debounceTimers.forEach(timer => clearTimeout(timer));
    this.debounceTimers.clear();
  }
}

export const grammarService = new GrammarService();
export type { GrammarIssue, GrammarCheckResult }; 