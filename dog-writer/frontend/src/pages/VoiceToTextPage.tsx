/**
 * Voice to Text Page
 * 
 * Clean, minimalist interface for voice-to-text functionality
 * with proper visual feedback and accessibility features.
 */

import React, { useState, useRef } from 'react';
import { logger } from '../utils/logger';

const VoiceToTextPage: React.FC = () => {
  const [isListening, setIsListening] = useState(false);
  const [transcript, setTranscript] = useState('');
  const [isSupported, setIsSupported] = useState(true);
  const recognitionRef = useRef<SpeechRecognition | null>(null);

  // Initialize speech recognition
  React.useEffect(() => {
    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
      const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
      recognitionRef.current = new SpeechRecognition();
      
      recognitionRef.current.continuous = true;
      recognitionRef.current.interimResults = true;
      recognitionRef.current.lang = 'en-US';

      recognitionRef.current.onresult = (event) => {
        let finalTranscript = '';
        for (let i = event.resultIndex; i < event.results.length; i++) {
          const result = event.results[i];
          if (result.isFinal) {
            finalTranscript += result[0].transcript;
          }
        }
        if (finalTranscript) {
          setTranscript(prev => prev + finalTranscript + ' ');
        }
      };

      recognitionRef.current.onerror = (event) => {
        logger.error('Speech recognition error:', event.error);
        setIsListening(false);
      };

      recognitionRef.current.onend = () => {
        setIsListening(false);
      };
    } else {
      setIsSupported(false);
    }
  }, []);

  const startListening = () => {
    if (recognitionRef.current && !isListening) {
      recognitionRef.current.start();
      setIsListening(true);
    }
  };

  const stopListening = () => {
    if (recognitionRef.current && isListening) {
      recognitionRef.current.stop();
      setIsListening(false);
    }
  };

  const clearTranscript = () => {
    setTranscript('');
  };

  const copyToClipboard = async () => {
    try {
      await navigator.clipboard.writeText(transcript);
      // Could add a toast notification here
    } catch (err) {
      logger.error('Failed to copy to clipboard:', err);
    }
  };

  if (!isSupported) {
    return (
      <div className="voice-page voice-page--unsupported">
        <div className="page-header">
          <h1 className="page-title">Voice to Text</h1>
          <p className="page-subtitle">Convert speech to text using your microphone</p>
        </div>
        
        <div className="unsupported-message">
          <div className="alert alert-error">
            <svg className="alert-icon" xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <circle cx="12" cy="12" r="10"></circle>
              <line x1="15" y1="9" x2="9" y2="15"></line>
              <line x1="9" y1="9" x2="15" y2="15"></line>
            </svg>
            <div>
              <h3>Speech Recognition Not Supported</h3>
              <p>Your browser doesn't support speech recognition. Please try using Chrome, Edge, or Safari.</p>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="voice-page">
      {/* Page Header */}
      <div className="page-header">
        <h1 className="page-title">Voice to Text</h1>
        <p className="page-subtitle">
          Convert speech to text using your microphone
        </p>
      </div>

      {/* Voice Controls */}
      <div className="voice-controls">
        <div className="voice-status">
          {isListening ? (
            <div className="listening-indicator">
              <div className="pulse-dot"></div>
              <span className="status-text">Listening...</span>
            </div>
          ) : (
            <span className="status-text text-secondary">Ready to listen</span>
          )}
        </div>

        <div className="control-buttons">
          {!isListening ? (
            <button 
              onClick={startListening}
              className="button-primary voice-button"
            >
              <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M12 2a3 3 0 0 0-3 3v7a3 3 0 0 0 6 0V5a3 3 0 0 0-3-3Z"></path>
                <path d="M19 10v2a7 7 0 0 1-14 0v-2"></path>
                <line x1="12" y1="19" x2="12" y2="23"></line>
                <line x1="8" y1="23" x2="16" y2="23"></line>
              </svg>
              Start Recording
            </button>
          ) : (
            <button 
              onClick={stopListening}
              className="button-secondary voice-button"
            >
              <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <rect width="18" height="18" x="3" y="3" rx="2" ry="2"></rect>
              </svg>
              Stop Recording
            </button>
          )}
        </div>
      </div>

      {/* Transcript Output */}
      <div className="transcript-section">
        <div className="transcript-header">
          <h2 className="section-title">Transcript</h2>
          <div className="transcript-actions">
            {transcript && (
              <>
                <button 
                  onClick={copyToClipboard}
                  className="button-ghost"
                  title="Copy to clipboard"
                >
                  <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                    <rect width="14" height="14" x="8" y="8" rx="2" ry="2"></rect>
                    <path d="M4 16c-1.1 0-2-.9-2-2V4c0-1.1.9-2 2-2h10c1.1 0 2 .9 2 2"></path>
                  </svg>
                  Copy
                </button>
                <button 
                  onClick={clearTranscript}
                  className="button-ghost"
                  title="Clear transcript"
                >
                  <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                    <path d="M3 6h18"></path>
                    <path d="M19 6v14c0 1-1 2-2 2H7c-1 0-2-1-2-2V6"></path>
                    <path d="M8 6V4c0-1 1-2 2-2h4c1 0 2 1 2 2v2"></path>
                  </svg>
                  Clear
                </button>
              </>
            )}
          </div>
        </div>

        <div className="transcript-output">
          {transcript ? (
            <div className="transcript-text">
              {transcript}
            </div>
          ) : (
            <div className="transcript-placeholder">
              <p className="text-secondary">
                Click "Start Recording" and begin speaking. Your words will appear here in real-time.
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default VoiceToTextPage; 