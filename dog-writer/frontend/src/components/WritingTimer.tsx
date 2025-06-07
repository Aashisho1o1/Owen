import React from 'react';
import { useWritingSession } from '../hooks/useWritingSession';

interface WritingTimerProps {
  editorRef?: React.RefObject<HTMLDivElement | null>;
  onSessionStart?: (sessionId: string) => void;
  onSessionEnd?: (summary: any) => void;
}

const WritingTimer: React.FC<WritingTimerProps> = ({ 
  editorRef, 
  onSessionStart, 
  onSessionEnd 
}) => {
  const writingSession = useWritingSession(editorRef);
  const {
    sessionId,
    isActive,
    currentActiveSeconds,
    currentFocusScore,
    timerVisible,
    startSession,
    endSession,
    toggleTimerVisibility,
    formatTime
  } = writingSession;

  // Handle session callbacks
  React.useEffect(() => {
    if (sessionId && onSessionStart) {
      onSessionStart(sessionId);
    }
  }, [sessionId, onSessionStart]);

  const handleStartSession = async () => {
    console.log('🖱️ Start session button clicked');
    const newSessionId = await startSession();
    console.log('🔄 Start session result:', newSessionId);
    if (newSessionId && onSessionStart) {
      onSessionStart(newSessionId);
    }
  };

  const handleEndSession = async () => {
    const summary = await endSession();
    if (summary && onSessionEnd) {
      onSessionEnd(summary);
    }
  };

  /**
   * FOCUS SCORE COLOR CODING
   * 
   * RATIONALE: Visual feedback helps writers understand their focus quality
   * without being judgmental. Green = great focus, yellow = good, orange = okay.
   * We avoid red to prevent negative feelings.
   */
  const getFocusScoreColor = (score: number) => {
    if (score >= 80) return '#10b981'; // Green - excellent focus
    if (score >= 60) return '#f59e0b'; // Amber - good focus  
    if (score >= 40) return '#f97316'; // Orange - moderate focus
    return '#6b7280'; // Gray - starting out or low focus
  };

  const getFocusScoreText = (score: number) => {
    if (score >= 80) return 'Excellent Focus';
    if (score >= 60) return 'Good Focus';
    if (score >= 40) return 'Moderate Focus';
    return 'Building Focus';
  };

  return (
    <div className="writing-timer-container">
      {/* Timer Toggle Button - Always Visible */}
      <button 
        className="timer-toggle-btn"
        onClick={toggleTimerVisibility}
        title={timerVisible ? "Hide writing timer" : "Show writing timer"}
        aria-label={timerVisible ? "Hide writing timer" : "Show writing timer"}
      >
        {timerVisible ? (
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"/>
            <line x1="1" y1="1" x2="23" y2="23"/>
          </svg>
        ) : (
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/>
            <circle cx="12" cy="12" r="3"/>
          </svg>
        )}
      </button>

      {/* Main Timer Display - Conditionally Visible */}
      {timerVisible && (
        <div className="timer-display">
          {!sessionId ? (
            /* Session Start State */
            <div className="session-start">
              <button 
                className="start-session-btn"
                onClick={handleStartSession}
                aria-label="Start writing session"
              >
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <polygon points="5,3 19,12 5,21"/>
                </svg>
                Start Writing
              </button>
              <span className="session-hint">Begin tracking your writing time</span>
            </div>
          ) : (
            /* Active Session State */
            <div className="session-active">
              {/* Primary Timer Display */}
              <div className="timer-main">
                <div className="timer-value">
                  {formatTime(currentActiveSeconds)}
                </div>
                <div className="timer-label">Active Writing</div>
              </div>

              {/* Focus Score Indicator */}
              <div className="focus-indicator">
                <div 
                  className="focus-bar"
                  style={{ 
                    width: `${Math.min(currentFocusScore, 100)}%`,
                    backgroundColor: getFocusScoreColor(currentFocusScore)
                  }}
                />
                <span className="focus-text">
                  {Math.round(currentFocusScore)}% {getFocusScoreText(currentFocusScore)}
                </span>
              </div>

              {/* Session Status */}
              <div className="session-status">
                <div className={`status-indicator ${isActive ? 'active' : 'paused'}`}>
                  <div className="status-dot" />
                  <span>{isActive ? 'Writing' : 'Thinking'}</span>
                </div>
                
                <button 
                  className="end-session-btn"
                  onClick={handleEndSession}
                  aria-label="End writing session"
                >
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <rect x="6" y="6" width="12" height="12"/>
                  </svg>
                  End Session
                </button>
              </div>
            </div>
          )}
        </div>
      )}

      <style>{`
        .writing-timer-container {
          position: fixed;
          top: 20px;
          right: 20px;
          z-index: 1000;
          font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif;
        }

        .timer-toggle-btn {
          position: absolute;
          top: 0;
          right: 0;
          width: 44px;
          height: 44px;
          border: none;
          border-radius: 22px;
          background: rgba(255, 255, 255, 0.9);
          backdrop-filter: blur(10px);
          box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
          cursor: pointer;
          display: flex;
          align-items: center;
          justify-content: center;
          color: #6b7280;
          transition: all 0.2s ease;
        }

        .timer-toggle-btn:hover {
          background: rgba(255, 255, 255, 0.95);
          color: #374151;
          transform: scale(1.05);
        }

        .timer-toggle-btn:active {
          transform: scale(0.95);
        }

        .timer-display {
          background: rgba(255, 255, 255, 0.95);
          backdrop-filter: blur(10px);
          border-radius: 16px;
          padding: 20px;
          margin-right: 60px;
          margin-top: 0;
          box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
          border: 1px solid rgba(255, 255, 255, 0.2);
          min-width: 240px;
          animation: slideIn 0.3s ease-out;
        }

        @keyframes slideIn {
          from { opacity: 0; transform: translateX(20px); }
          to { opacity: 1; transform: translateX(0); }
        }

        /* Session Start State */
        .session-start {
          text-align: center;
        }

        .start-session-btn {
          display: flex;
          align-items: center;
          gap: 8px;
          background: #10b981;
          color: white;
          border: none;
          border-radius: 12px;
          padding: 12px 20px;
          font-size: 14px;
          font-weight: 600;
          cursor: pointer;
          transition: all 0.2s ease;
          width: 100%;
          justify-content: center;
        }

        .start-session-btn:hover {
          background: #059669;
          transform: translateY(-1px);
        }

        .session-hint {
          display: block;
          margin-top: 8px;
          font-size: 12px;
          color: #6b7280;
        }

        /* Active Session State */
        .session-active {
          display: flex;
          flex-direction: column;
          gap: 16px;
        }

        .timer-main {
          text-align: center;
        }

        .timer-value {
          font-size: 32px;
          font-weight: 700;
          color: #1f2937;
          font-variant-numeric: tabular-nums;
          line-height: 1;
        }

        .timer-label {
          font-size: 12px;
          color: #6b7280;
          text-transform: uppercase;
          letter-spacing: 0.05em;
          margin-top: 4px;
          font-weight: 500;
        }

        /* Focus Score Indicator */
        .focus-indicator {
          position: relative;
        }

        .focus-bar {
          height: 6px;
          border-radius: 3px;
          background: #10b981;
          transition: all 0.3s ease;
          position: relative;
          overflow: hidden;
        }

        .focus-bar::before {
          content: '';
          position: absolute;
          top: 0;
          left: 0;
          right: 0;
          bottom: 0;
          background: rgba(255, 255, 255, 0.2);
          border-radius: 3px;
        }

        .focus-text {
          font-size: 11px;
          color: #6b7280;
          margin-top: 6px;
          display: block;
          font-weight: 500;
        }

        /* Session Status */
        .session-status {
          display: flex;
          align-items: center;
          justify-content: space-between;
        }

        .status-indicator {
          display: flex;
          align-items: center;
          gap: 6px;
          font-size: 12px;
          font-weight: 500;
        }

        .status-indicator.active {
          color: #10b981;
        }

        .status-indicator.paused {
          color: #f59e0b;
        }

        .status-dot {
          width: 6px;
          height: 6px;
          border-radius: 50%;
          background: currentColor;
        }

        .status-indicator.active .status-dot {
          animation: pulse 2s infinite;
        }

        @keyframes pulse {
          0%, 100% { opacity: 1; }
          50% { opacity: 0.5; }
        }

        .end-session-btn {
          display: flex;
          align-items: center;
          gap: 6px;
          background: transparent;
          color: #6b7280;
          border: 1px solid #e5e7eb;
          border-radius: 8px;
          padding: 6px 12px;
          font-size: 12px;
          cursor: pointer;
          transition: all 0.2s ease;
        }

        .end-session-btn:hover {
          background: #f9fafb;
          color: #374151;
          border-color: #d1d5db;
        }

        /* Mobile Responsive */
        @media (max-width: 768px) {
          .writing-timer-container {
            top: 10px;
            right: 10px;
          }

          .timer-display {
            margin-right: 50px;
            min-width: 200px;
            padding: 16px;
          }

          .timer-value {
            font-size: 24px;
          }

          .timer-toggle-btn {
            width: 40px;
            height: 40px;
          }
        }

        /* Dark mode support */
        @media (prefers-color-scheme: dark) {
          .timer-display {
            background: rgba(31, 41, 55, 0.95);
            border: 1px solid rgba(55, 65, 81, 0.3);
          }

          .timer-toggle-btn {
            background: rgba(31, 41, 55, 0.9);
            color: #9ca3af;
          }

          .timer-toggle-btn:hover {
            background: rgba(31, 41, 55, 0.95);
            color: #d1d5db;
          }

          .timer-value {
            color: #f9fafb;
          }

          .timer-label {
            color: #9ca3af;
          }

          .focus-text {
            color: #9ca3af;
          }

          .end-session-btn {
            border-color: #4b5563;
            color: #9ca3af;
          }

          .end-session-btn:hover {
            background: rgba(55, 65, 81, 0.5);
            color: #d1d5db;
            border-color: #6b7280;
          }
        }
      `}</style>
    </div>
  );
};

export default WritingTimer; 