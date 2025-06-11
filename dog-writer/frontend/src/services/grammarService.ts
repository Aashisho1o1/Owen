/**
 * Grammar Checking Service
 * 
 * Provides real-time grammar and spelling checking with speculative execution:
 * - Fast checks for immediate feedback (typing)
 * - Comprehensive checks for final review
 * - Smart caching and debouncing
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
  overall_score?: number;
  style_notes?: string;
}

class GrammarService {
  private cache = new Map<string, { result: GrammarCheckResult; timestamp: number }>();
  private debounceTimers = new Map<string, NodeJS.Timeout>();
  private lastChecks = new Map<string, number>();
  
  private readonly CACHE_TTL = 5 * 60 * 1000; // 5 minutes
  private readonly DEBOUNCE_DELAY = 500; // 500ms
  private readonly API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

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
      const response = await fetch(`${this.API_BASE_URL}/api/grammar/check`, {
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
      
      this.lastChecks.set(textHash, Date.now());
      return result;
      
    } catch (error) {
      console.error('Real-time grammar check failed:', error);
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
      const response = await fetch(`${this.API_BASE_URL}/api/grammar/check`, {
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
      console.error('Comprehensive grammar check failed:', error);
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
      const response = await fetch(`${this.API_BASE_URL}/api/grammar/check-stream`, {
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
      
      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      
      while (true) {
        const { done, value } = await reader.read();
        
        if (done) break;
        
        const chunk = decoder.decode(value);
        const lines = chunk.split('\n');
        
        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const data = JSON.parse(line.slice(6));
              
              if (data.type === 'complete') {
                return;
              } else if (data.type === 'error') {
                throw new Error(data.message);
              } else if (data.issues) {
                onUpdate(data.issues, data.type);
              }
            } catch (e) {
              console.error('Error parsing stream data:', e);
            }
          }
        }
      }
    } catch (error) {
      console.error('Streaming grammar check failed:', error);
    }
  }
  
  /**
   * Debounced real-time checking for editor integration
   */
  checkRealTimeDebounced(
    text: string, 
    callback: (result: GrammarCheckResult) => void,
    delay = this.DEBOUNCE_DELAY
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
    
    const isExpired = Date.now() - cached.timestamp > this.CACHE_TTL;
    if (isExpired) {
      this.cache.delete(textHash);
      return null;
    }
    
    return cached.result;
  }
  
  private shouldDebounce(textHash: string): boolean {
    const lastCheck = this.lastChecks.get(textHash);
    if (!lastCheck) return false;
    
    return Date.now() - lastCheck < this.DEBOUNCE_DELAY;
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
    this.lastChecks.clear();
    
    // Clear all debounce timers
    this.debounceTimers.forEach(timer => clearTimeout(timer));
    this.debounceTimers.clear();
  }
}

export const grammarService = new GrammarService();
export type { GrammarIssue, GrammarCheckResult }; 