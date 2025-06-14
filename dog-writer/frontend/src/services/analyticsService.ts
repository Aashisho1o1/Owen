/**
 * Analytics Service for DOG Writer Frontend
 * Privacy-compliant user behavior tracking and writing analytics integration
 */

interface AnalyticsConfig {
  apiBaseUrl: string;
  enableTracking: boolean;
  respectDoNotTrack: boolean;
  sessionTimeout: number;
}

interface ConsentPreferences {
  essential: boolean;
  analytics: boolean;
  comprehensive: boolean;
}

interface WritingSession {
  documentId: string;
  contentBefore: string;
  contentAfter: string;
  sessionDurationMinutes: number;
}

interface EventProperties {
  [key: string]: any;
}

interface WritingInsights {
  user_id: string;
  writing_summary: {
    total_sessions: number;
    average_typing_speed: number;
    average_readability: number;
    average_complexity: number;
  };
  strengths: string[];
  improvement_areas: string[];
  recommendations: string[];
  writing_style_summary: string;
}

interface StyleAnalysis {
  analysis: {
    readability_score: number;
    flesch_kincaid_grade: number;
    avg_sentence_length: number;
    avg_word_length: number;
    vocabulary_diversity: number;
    passive_voice_ratio: number;
    sentiment_polarity: number;
    sentiment_subjectivity: number;
    complexity_score: number;
    tone_analysis: Record<string, number>;
    writing_voice_indicators: Record<string, any>;
  };
  interpretation: {
    readability: string;
    sentiment: string;
    complexity: string;
  };
}

class AnalyticsService {
  private config: AnalyticsConfig;
  private sessionId: string;
  private userId: string | null = null;
  private consentPreferences: ConsentPreferences | null = null;
  private eventQueue: Array<{ event: string; properties: EventProperties; timestamp: number }> = [];
  private flushTimer: NodeJS.Timeout | null = null;

  constructor(config: Partial<AnalyticsConfig> = {}) {
    this.config = {
      apiBaseUrl: config.apiBaseUrl || '/api',
      enableTracking: config.enableTracking !== false,
      respectDoNotTrack: config.respectDoNotTrack !== false,
      sessionTimeout: config.sessionTimeout || 30 * 60 * 1000, // 30 minutes
    };

    this.sessionId = this.generateSessionId();
    this.initializeTracking();
  }

  private generateSessionId(): string {
    const randomBytes = new Uint32Array(1);
    window.crypto.getRandomValues(randomBytes);
    const randomSuffix = randomBytes[0].toString(36);
    return `session_${Date.now()}_${randomSuffix}`;
  }

  private initializeTracking(): void {
    // Check Do Not Track preference
    if (this.config.respectDoNotTrack && navigator.doNotTrack === '1') {
      this.config.enableTracking = false;
      console.log('Analytics disabled due to Do Not Track preference');
      return;
    }

    // Load consent preferences from localStorage
    this.loadConsentPreferences();

    // Set up session management
    this.setupSessionManagement();

    // Start event queue flushing
    this.startEventQueueFlushing();

    // Track page load
    this.trackEvent('page_load', {
      url: window.location.href,
      referrer: document.referrer,
      user_agent: navigator.userAgent,
    });
  }

  private loadConsentPreferences(): void {
    try {
      const stored = localStorage.getItem('analytics_consent');
      if (stored) {
        this.consentPreferences = JSON.parse(stored);
      }
    } catch (error) {
      console.warn('Failed to load consent preferences:', error);
    }
  }

  private saveConsentPreferences(): void {
    if (this.consentPreferences) {
      try {
        localStorage.setItem('analytics_consent', JSON.stringify(this.consentPreferences));
      } catch (error) {
        console.warn('Failed to save consent preferences:', error);
      }
    }
  }

  private setupSessionManagement(): void {
    // Add session ID to all requests
    const originalFetch = window.fetch;
    window.fetch = (input: RequestInfo | URL, init?: RequestInit) => {
      const headers = new Headers(init?.headers);
      headers.set('X-Session-ID', this.sessionId);
      
      return originalFetch(input, {
        ...init,
        headers,
      });
    };

    // Track session activity
    let lastActivity = Date.now();
    const updateActivity = () => {
      lastActivity = Date.now();
    };

    ['mousedown', 'mousemove', 'keypress', 'scroll', 'touchstart'].forEach(event => {
      document.addEventListener(event, updateActivity, { passive: true });
    });

    // Check for session timeout
    setInterval(() => {
      if (Date.now() - lastActivity > this.config.sessionTimeout) {
        this.trackEvent('session_timeout');
        this.sessionId = this.generateSessionId();
        lastActivity = Date.now();
      }
    }, 60000); // Check every minute
  }

  private startEventQueueFlushing(): void {
    this.flushTimer = setInterval(() => {
      this.flushEventQueue();
    }, 5000); // Flush every 5 seconds
  }

  private async flushEventQueue(): Promise<void> {
    if (this.eventQueue.length === 0) return;

    const events = [...this.eventQueue];
    this.eventQueue = [];

    try {
      for (const event of events) {
        await this.sendEvent(event.event, event.properties);
      }
    } catch (error) {
      console.warn('Failed to flush event queue:', error);
      // Re-add events to queue for retry
      this.eventQueue.unshift(...events);
    }
  }

  private async sendEvent(eventName: string, properties: EventProperties): Promise<void> {
    if (!this.config.enableTracking) return;

    try {
      const response = await fetch(`${this.config.apiBaseUrl}/analytics/track-event`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-Session-ID': this.sessionId,
        },
        body: JSON.stringify({
          event_name: eventName,
          properties: {
            ...properties,
            session_id: this.sessionId,
            timestamp: new Date().toISOString(),
          },
        }),
      });

      if (!response.ok) {
        throw new Error(`Analytics request failed: ${response.status}`);
      }
    } catch (error) {
      console.warn('Failed to send analytics event:', error);
      throw error;
    }
  }

  // Public API Methods

  /**
   * Set user consent preferences
   */
  async setConsent(preferences: ConsentPreferences): Promise<void> {
    this.consentPreferences = preferences;
    this.saveConsentPreferences();

    try {
      const response = await fetch(`${this.config.apiBaseUrl}/analytics/consent`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(preferences),
      });

      if (!response.ok) {
        throw new Error(`Failed to set consent: ${response.status}`);
      }

      this.trackEvent('consent_updated', preferences);
    } catch (error) {
      console.error('Failed to set consent preferences:', error);
      throw error;
    }
  }

  /**
   * Get current consent preferences
   */
  async getConsent(): Promise<ConsentPreferences | null> {
    try {
      const response = await fetch(`${this.config.apiBaseUrl}/analytics/consent`);
      
      if (response.ok) {
        const data = await response.json();
        this.consentPreferences = {
          essential: data.essential,
          analytics: data.analytics,
          comprehensive: data.comprehensive,
        };
        this.saveConsentPreferences();
        return this.consentPreferences;
      }
    } catch (error) {
      console.warn('Failed to get consent preferences:', error);
    }

    return this.consentPreferences;
  }

  /**
   * Track a custom event
   */
  trackEvent(eventName: string, properties: EventProperties = {}): void {
    if (!this.config.enableTracking) return;

    // Check consent for this type of event
    if (!this.hasConsentForEvent(eventName)) return;

    this.eventQueue.push({
      event: eventName,
      properties: {
        ...properties,
        session_id: this.sessionId,
      },
      timestamp: Date.now(),
    });
  }

  /**
   * Track writing session
   */
  async trackWritingSession(session: WritingSession): Promise<void> {
    if (!this.config.enableTracking || !this.hasConsentForEvent('writing_session')) return;

    try {
      const response = await fetch(`${this.config.apiBaseUrl}/analytics/writing/session`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(session),
      });

      if (!response.ok) {
        throw new Error(`Failed to track writing session: ${response.status}`);
      }

      const result = await response.json();
      return result;
    } catch (error) {
      console.error('Failed to track writing session:', error);
      throw error;
    }
  }

  /**
   * Get writing insights
   */
  async getWritingInsights(): Promise<WritingInsights | null> {
    try {
      const response = await fetch(`${this.config.apiBaseUrl}/analytics/writing/insights`);
      
      if (response.ok) {
        return await response.json();
      }
    } catch (error) {
      console.error('Failed to get writing insights:', error);
    }

    return null;
  }

  /**
   * Analyze writing style
   */
  async analyzeWritingStyle(text: string): Promise<StyleAnalysis | null> {
    if (text.length < 50) {
      throw new Error('Text must be at least 50 characters long for analysis');
    }

    try {
      const response = await fetch(
        `${this.config.apiBaseUrl}/analytics/writing/style-analysis?text=${encodeURIComponent(text)}`
      );
      
      if (response.ok) {
        return await response.json();
      }
    } catch (error) {
      console.error('Failed to analyze writing style:', error);
    }

    return null;
  }

  /**
   * Get analytics dashboard data
   */
  async getDashboardData(days: number = 30): Promise<any> {
    try {
      const response = await fetch(`${this.config.apiBaseUrl}/analytics/dashboard?days=${days}`);
      
      if (response.ok) {
        return await response.json();
      }
    } catch (error) {
      console.error('Failed to get dashboard data:', error);
    }

    return null;
  }

  /**
   * Export user data (GDPR compliance)
   */
  async exportUserData(): Promise<any> {
    try {
      const response = await fetch(`${this.config.apiBaseUrl}/analytics/export-data`);
      
      if (response.ok) {
        return await response.json();
      }
    } catch (error) {
      console.error('Failed to export user data:', error);
      throw error;
    }
  }

  /**
   * Delete user data (GDPR compliance)
   */
  async deleteUserData(): Promise<boolean> {
    try {
      const response = await fetch(`${this.config.apiBaseUrl}/analytics/delete-data?confirm=true`, {
        method: 'DELETE',
      });
      
      if (response.ok) {
        // Clear local data
        localStorage.removeItem('analytics_consent');
        this.consentPreferences = null;
        this.eventQueue = [];
        return true;
      }
    } catch (error) {
      console.error('Failed to delete user data:', error);
    }

    return false;
  }

  /**
   * Track button clicks automatically
   */
  setupButtonTracking(): void {
    document.addEventListener('click', (event) => {
      const target = event.target as HTMLElement;
      
      if (target.tagName === 'BUTTON' || target.closest('button')) {
        const button = target.tagName === 'BUTTON' ? target : target.closest('button');
        const buttonText = button?.textContent?.trim() || 'Unknown';
        const buttonId = button?.id || 'no-id';
        const buttonClass = button?.className || 'no-class';

        this.trackEvent('button_click', {
          button_text: buttonText,
          button_id: buttonId,
          button_class: buttonClass,
          page_url: window.location.href,
        });
      }
    });
  }

  /**
   * Track form submissions
   */
  setupFormTracking(): void {
    document.addEventListener('submit', (event) => {
      const form = event.target as HTMLFormElement;
      const formId = form.id || 'no-id';
      const formClass = form.className || 'no-class';

      this.trackEvent('form_submit', {
        form_id: formId,
        form_class: formClass,
        page_url: window.location.href,
      });
    });
  }

  /**
   * Track page views for SPA navigation
   */
  trackPageView(path?: string): void {
    this.trackEvent('page_view', {
      path: path || window.location.pathname,
      url: window.location.href,
      referrer: document.referrer,
    });
  }

  private hasConsentForEvent(eventName: string): boolean {
    if (!this.consentPreferences) {
      // Default to essential only if no consent given
      return ['page_load', 'page_view', 'session_timeout'].includes(eventName);
    }

    // Essential events (always allowed if essential consent given)
    const essentialEvents = ['page_load', 'page_view', 'session_timeout', 'consent_updated'];
    if (essentialEvents.includes(eventName)) {
      return this.consentPreferences.essential;
    }

    // Analytics events (require analytics consent)
    const analyticsEvents = ['button_click', 'form_submit', 'document_created', 'document_saved'];
    if (analyticsEvents.includes(eventName)) {
      return this.consentPreferences.analytics;
    }

    // Comprehensive events (require comprehensive consent)
    const comprehensiveEvents = ['writing_session', 'ai_chat_message', 'text_analysis'];
    if (comprehensiveEvents.includes(eventName)) {
      return this.consentPreferences.comprehensive;
    }

    // Default to analytics consent for unknown events
    return this.consentPreferences.analytics;
  }

  /**
   * Clean up resources
   */
  destroy(): void {
    if (this.flushTimer) {
      clearInterval(this.flushTimer);
      this.flushTimer = null;
    }

    // Flush remaining events
    this.flushEventQueue();
  }
}

// Create and export singleton instance
export const analyticsService = new AnalyticsService({
  apiBaseUrl: import.meta.env.VITE_API_BASE_URL || '/api',
  enableTracking: import.meta.env.VITE_ENABLE_ANALYTICS !== 'false',
});

// Auto-setup tracking when service is imported
analyticsService.setupButtonTracking();
analyticsService.setupFormTracking();

export default analyticsService; 