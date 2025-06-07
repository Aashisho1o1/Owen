import { useState, useEffect, useRef, useCallback } from 'react';

interface WritingSessionState {
  sessionId: string | null;
  isActive: boolean;
  currentActiveSeconds: number;
  sessionStartTime: string | null;
  lastActivityTime: string | null;
  currentFocusScore: number;
  keystrokes: number;
  timerVisible: boolean;
}

interface WriteSessionConfig {
  // Research-backed timeout values from our discussion
  activityBridgeTimeout: number;    // 30 seconds - thinking pause grace period
  gracePeriodOnBlur: number;        // 5 seconds - tab switch grace period  
  sessionEndTimeout: number;        // 1800 seconds (30 minutes) - auto-end session
  autoSaveInterval: number;         // 5 seconds - how often to send activity updates
}

const DEFAULT_CONFIG: WriteSessionConfig = {
  activityBridgeTimeout: 30 * 1000,    // 30 seconds
  gracePeriodOnBlur: 5 * 1000,         // 5 seconds
  sessionEndTimeout: 30 * 60 * 1000,   // 30 minutes
  autoSaveInterval: 5 * 1000,          // 5 seconds
};

export const useWritingSession = (
  editorRef?: React.RefObject<HTMLDivElement | null>,
  config: Partial<WriteSessionConfig> = {}
) => {
  const fullConfig = { ...DEFAULT_CONFIG, ...config };
  
  // Session state
  const [sessionState, setSessionState] = useState<WritingSessionState>({
    sessionId: null,
    isActive: false,
    currentActiveSeconds: 0,
    sessionStartTime: null,
    lastActivityTime: null,
    currentFocusScore: 0,
    keystrokes: 0,
    timerVisible: true, // Default to visible
  });

  // Refs for timer management
  const activityBridgeTimer = useRef<ReturnType<typeof setTimeout> | null>(null);
  const gracePeriodTimer = useRef<ReturnType<typeof setTimeout> | null>(null);
  const sessionEndTimer = useRef<ReturnType<typeof setTimeout> | null>(null);
  const autoSaveTimer = useRef<ReturnType<typeof setTimeout> | null>(null);
  const liveUpdateTimer = useRef<ReturnType<typeof setInterval> | null>(null);
  const lastActivityRef = useRef<Date>(new Date());
  const sessionStartRef = useRef<Date | null>(null);
  const totalKeystrokesRef = useRef<number>(0);
  const isWindowFocusedRef = useRef<boolean>(true);

  // Declare endSession first to avoid circular dependency
  const endSession = useCallback(async () => {
    if (!sessionState.sessionId || !sessionStartRef.current) return;

    try {
      const response = await fetch('/api/sessions/end', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          session_id: sessionState.sessionId,
          total_active_seconds: sessionState.currentActiveSeconds,
          total_keystrokes: totalKeystrokesRef.current,
          total_words: editorRef?.current?.textContent?.split(/\s+/).length || 0
        })
      });

      const data = await response.json();
      
      if (data.success) {
        console.log('Session ended:', data.session_summary);
        
        // Reset state
        setSessionState(prev => ({
          ...prev,
          sessionId: null,
          isActive: false,
          currentActiveSeconds: 0,
          currentFocusScore: 0,
          keystrokes: 0
        }));

        sessionStartRef.current = null;
        totalKeystrokesRef.current = 0;

        return data.session_summary;
      }
    } catch (error) {
      console.error('Error ending session:', error);
    }
    return null;
  }, [sessionState.sessionId, sessionState.currentActiveSeconds, editorRef]);

  /**
   * CORE ACTIVITY DETECTION SYSTEM
   * 
   * RATIONALE: This is the heart of our productivity tracking. We define
   * "active writing" as actual engagement with the writing process, not
   * just having the tab open.
   * 
   * ACTIVITY TYPES:
   * 1. Typing - Core writing activity (keydown events)
   * 2. Editing - Text manipulation (delete, cut, paste)
   * 3. Scrolling - Content review (scrolling within editor)
   * 4. Thinking Pause - Brief pause that's still productive
   * 
   * BRIDGING LOGIC:
   * When activity stops, we start an "activity bridge" timer. If new activity
   * occurs before it expires, the pause is considered "thinking time" and
   * remains part of active writing. This prevents penalizing natural pauses.
   */

  const recordActivity = useCallback(async (activityType: string) => {
    if (!sessionState.sessionId) return;

    const now = new Date();
    lastActivityRef.current = now;

    // Clear any existing activity bridge timer
    if (activityBridgeTimer.current) {
      clearTimeout(activityBridgeTimer.current);
      activityBridgeTimer.current = null;
    }

    // Update local state
    setSessionState(prev => ({
      ...prev,
      isActive: true,
      lastActivityTime: now.toISOString(),
      keystrokes: activityType === 'typing' ? prev.keystrokes + 1 : prev.keystrokes
    }));

    // Update keystroke counter
    if (activityType === 'typing') {
      totalKeystrokesRef.current += 1;
    }

    // Send activity update to backend (throttled by autoSaveTimer)
    try {
      await fetch('/api/sessions/activity', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          session_id: sessionState.sessionId,
          activity_type: activityType,
          content_length: editorRef?.current?.textContent?.length || 0
        })
      });
    } catch (error) {
      console.error('Error recording activity:', error);
    }

    // Start activity bridge timer for thinking pauses
    activityBridgeTimer.current = setTimeout(() => {
      setSessionState(prev => ({ ...prev, isActive: false }));
      recordActivity('thinking_pause');
    }, fullConfig.activityBridgeTimeout);

  }, [sessionState.sessionId, fullConfig.activityBridgeTimeout, editorRef]);

  /**
   * WINDOW FOCUS MANAGEMENT
   * 
   * RATIONALE: Writers may briefly switch tabs for research or reference.
   * We provide a small grace period before considering this a focus break.
   * 
   * GRACE PERIOD: 5 seconds allows for quick tab switches that are part of
   * the writing flow (checking a definition, quick reference, etc.)
   */

  const handleWindowBlur = useCallback(() => {
    isWindowFocusedRef.current = false;
    
    // Start grace period timer
    gracePeriodTimer.current = setTimeout(() => {
      if (sessionState.sessionId) {
        recordActivity('focus_lost');
      }
    }, fullConfig.gracePeriodOnBlur);
  }, [sessionState.sessionId, fullConfig.gracePeriodOnBlur, recordActivity]);

  const handleWindowFocus = useCallback(() => {
    isWindowFocusedRef.current = true;
    
    // Clear grace period if we regained focus quickly
    if (gracePeriodTimer.current) {
      clearTimeout(gracePeriodTimer.current);
      gracePeriodTimer.current = null;
    } else if (sessionState.sessionId) {
      // We were actually away, so record focus regained
      recordActivity('focus_regained');
    }
  }, [sessionState.sessionId, recordActivity]);

  /**
   * EVENT LISTENERS SETUP
   * 
   * RATIONALE: We need to listen for various user interactions to determine
   * when they're actively writing vs. idle. Different events indicate
   * different types of engagement.
   * 
   * PERFORMANCE: We throttle high-frequency events like scroll to avoid
   * overwhelming the system while still capturing meaningful activity.
   */

  const setupEventListeners = useCallback(() => {
    const editor = editorRef?.current;
    if (!editor) return () => {};

    let scrollTimeout: ReturnType<typeof setTimeout>;
    
    // Typing activity (most important indicator)
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key.length === 1 || ['Backspace', 'Delete'].includes(e.key)) {
        recordActivity('typing');
      }
    };

    // Editing activity (cursor movement, selection)
    const handleClick = () => recordActivity('editing');

    // Content review activity (throttled scroll)
    const handleScroll = () => {
      clearTimeout(scrollTimeout);
      scrollTimeout = setTimeout(() => recordActivity('scrolling'), 500);
    };

    // Tab visibility changes
    const handleVisibilityChange = () => {
      if (document.hidden) {
        handleWindowBlur();
      } else {
        handleWindowFocus();
      }
    };

    // Add event listeners
    editor.addEventListener('keydown', handleKeyDown);
    editor.addEventListener('click', handleClick);
    editor.addEventListener('scroll', handleScroll);
    document.addEventListener('visibilitychange', handleVisibilityChange);
    window.addEventListener('blur', handleWindowBlur);
    window.addEventListener('focus', handleWindowFocus);

    // Cleanup function
    return () => {
      editor.removeEventListener('keydown', handleKeyDown);
      editor.removeEventListener('click', handleClick);
      editor.removeEventListener('scroll', handleScroll);
      document.removeEventListener('visibilitychange', handleVisibilityChange);
      window.removeEventListener('blur', handleWindowBlur);
      window.removeEventListener('focus', handleWindowFocus);
      clearTimeout(scrollTimeout);
    };
  }, [editorRef, recordActivity, handleWindowBlur, handleWindowFocus]);

  /**
   * SESSION MANAGEMENT FUNCTIONS
   */

  const startSession = useCallback(async () => {
    try {
      console.log('🎬 Starting writing session...');
      
      const response = await fetch('/api/sessions/start', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          content_length: editorRef?.current?.textContent?.length || 0
        })
      });

      console.log('📡 Session start response status:', response.status);
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const data = await response.json();
      console.log('📝 Session start response data:', data);
      
      if (data.success) {
        const now = new Date();
        sessionStartRef.current = now;
        totalKeystrokesRef.current = 0;

        setSessionState(prev => ({
          ...prev,
          sessionId: data.session_id,
          isActive: true,
          sessionStartTime: now.toISOString(),
          lastActivityTime: now.toISOString(),
          currentActiveSeconds: 0,
          currentFocusScore: 0,
          keystrokes: 0
        }));

        // Start session end timer (auto-end after 30 minutes of inactivity)
        sessionEndTimer.current = setTimeout(() => {
          console.log('⏰ Session auto-ending due to inactivity');
          endSession();
        }, fullConfig.sessionEndTimeout);

        console.log(`✅ Writing session started successfully: ${data.session_id}`);
        return data.session_id;
      } else {
        throw new Error(data.message || 'Unknown error from server');
      }
    } catch (error) {
      console.error('❌ Error starting session:', error);
      
      // Show a user-friendly error message
      alert(`Failed to start writing session: ${error instanceof Error ? error.message : 'Unknown error'}`);
      
      return null;
    }
  }, [editorRef, fullConfig.sessionEndTimeout, endSession]);

  /**
   * LIVE TIMER UPDATES
   * 
   * RATIONALE: Updates the timer display every second when active.
   * This provides real-time feedback to writers about their active time.
   */

  const updateLiveTimer = useCallback(async () => {
    if (!sessionState.sessionId) return;

    try {
      const response = await fetch(`/api/sessions/live/${sessionState.sessionId}`);
      const data = await response.json();

      setSessionState(prev => ({
        ...prev,
        currentActiveSeconds: data.current_active_seconds,
        currentFocusScore: data.current_focus_score,
        isActive: data.is_active
      }));
    } catch (error) {
      console.error('Error updating live timer:', error);
    }
  }, [sessionState.sessionId]);

  const toggleTimerVisibility = useCallback(() => {
    setSessionState(prev => ({
      ...prev,
      timerVisible: !prev.timerVisible
    }));
    
    // Save preference to localStorage
    localStorage.setItem('writing-timer-visible', (!sessionState.timerVisible).toString());
  }, [sessionState.timerVisible]);

  /**
   * UTILITY FUNCTIONS
   */

  const formatTime = useCallback((seconds: number): string => {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = seconds % 60;
    
    if (hours > 0) {
      return `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
    }
    return `${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  }, []);

  const getSessionStats = useCallback(() => {
    if (!sessionStartRef.current) return null;

    const now = new Date();
    const totalDuration = (now.getTime() - sessionStartRef.current.getTime()) / 1000;
    const focusScore = sessionState.currentActiveSeconds / totalDuration * 100;

    return {
      activeTime: formatTime(sessionState.currentActiveSeconds),
      totalTime: formatTime(Math.floor(totalDuration)),
      focusScore: Math.round(focusScore),
      keystrokes: totalKeystrokesRef.current,
      wordsWritten: editorRef?.current?.textContent?.split(/\s+/).length || 0
    };
  }, [sessionState.currentActiveSeconds, formatTime, editorRef]);

  /**
   * EFFECTS FOR SETUP AND CLEANUP
   */

  // Setup event listeners when editor is available
  useEffect(() => {
    if (editorRef?.current) {
      const cleanup = setupEventListeners();
      return cleanup;
    }
  }, [setupEventListeners, editorRef]);

  // Load timer visibility preference
  useEffect(() => {
    const saved = localStorage.getItem('writing-timer-visible');
    if (saved !== null) {
      setSessionState(prev => ({
        ...prev,
        timerVisible: saved === 'true'
      }));
    }
  }, []);

  // Live timer updates
  useEffect(() => {
    if (sessionState.sessionId && sessionState.timerVisible) {
      liveUpdateTimer.current = setInterval(updateLiveTimer, 1000);
      return () => {
        if (liveUpdateTimer.current) {
          clearInterval(liveUpdateTimer.current);
        }
      };
    }
  }, [sessionState.sessionId, sessionState.timerVisible, updateLiveTimer]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      // Clear all timers
      if (activityBridgeTimer.current) clearTimeout(activityBridgeTimer.current);
      if (gracePeriodTimer.current) clearTimeout(gracePeriodTimer.current);
      if (sessionEndTimer.current) clearTimeout(sessionEndTimer.current);
      if (autoSaveTimer.current) clearTimeout(autoSaveTimer.current);
      if (liveUpdateTimer.current) clearInterval(liveUpdateTimer.current);

      // End session if active
      if (sessionState.sessionId) {
        endSession();
      }
    };
  }, [sessionState.sessionId, endSession]);

  return {
    // Session state
    ...sessionState,
    
    // Session management
    startSession,
    endSession,
    
    // Timer controls
    toggleTimerVisibility,
    formatTime: (seconds: number) => formatTime(seconds),
    
    // Analytics
    getSessionStats,
    
    // Configuration
    config: fullConfig
  };
}; 