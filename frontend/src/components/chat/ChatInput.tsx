/**
 * ChatInput Component - Enhanced Conversational Interface
 * 
 * Handles user input for chat messages with keyboard shortcuts,
 * contextual suggested questions, and improved visual feedback.
 */

import React, { useState, useRef, useEffect } from 'react';

interface ChatInputProps {
  onSendMessage: (message: string) => void;
  isDisabled?: boolean;
  suggestedQuestions?: string[];
  highlightedText?: string;
}

export const ChatInput: React.FC<ChatInputProps> = ({ 
  onSendMessage, 
  isDisabled = false, 
  suggestedQuestions = [],
  highlightedText 
}) => {
  const [message, setMessage] = useState('');
  const [isMobile, setIsMobile] = useState(false);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // Check if screen is mobile size
  useEffect(() => {
    const checkMobile = () => {
      setIsMobile(window.innerWidth <= 768);
    };

    checkMobile();
    window.addEventListener('resize', checkMobile);
    return () => window.removeEventListener('resize', checkMobile);
  }, []);

  // Auto-resize textarea
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${textareaRef.current.scrollHeight}px`;
    }
  }, [message]);

  // Focus textarea when component mounts or becomes enabled
  useEffect(() => {
    if (textareaRef.current && !isDisabled) {
      textareaRef.current.focus();
    }
  }, [isDisabled]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (message.trim() && !isDisabled) {
      onSendMessage(message.trim());
      setMessage('');
      // Refocus the textarea after sending
      setTimeout(() => {
        if (textareaRef.current) {
          textareaRef.current.focus();
        }
      }, 100);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    // Send message on Ctrl+Enter or Cmd+Enter
    if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  const handleSuggestedQuestion = (question: string) => {
    setMessage(question);
    if (textareaRef.current) {
      textareaRef.current.focus();
      // Move cursor to end
      setTimeout(() => {
        if (textareaRef.current) {
          textareaRef.current.setSelectionRange(question.length, question.length);
        }
      }, 0);
    }
  };

  // Mobile-specific: Limit suggested questions to 2 on mobile devices
  const getMobileSuggestedQuestions = () => {
    if (isMobile) {
      return suggestedQuestions.slice(0, 2); // Show only 2 questions on mobile
    }
    return suggestedQuestions; // Show all questions on desktop
  };

  const getPlaceholderText = () => {
    if (highlightedText) {
      return "Ask about the selected text or type your own question...";
    }
    return "Type your writing question here...";
  };

  const getInputHelperText = () => {
    if (highlightedText) {
      return `🎯 AI will focus on your ${highlightedText.split(/\s+/).length} word selection`;
    }
    return ""; // Removed the keyboard shortcut and AI analyze text
  };

  return (
    <div className="chat-input-container">
      {/* Suggested Questions - Only show when no text is highlighted */}
      {getMobileSuggestedQuestions().length > 0 && !highlightedText && (
        <div className="suggested-questions">
          <div className="suggested-questions-title">
            Suggested questions:
          </div>
          <div className="suggested-questions-list">
            {getMobileSuggestedQuestions().map((question, index) => (
              <button
                key={index}
                className="suggested-question-button"
                onClick={() => handleSuggestedQuestion(question)}
                disabled={isDisabled}
                title={`Click to use this question: ${question}`}
              >
                {question}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Input Form */}
      <form onSubmit={handleSubmit} className="chat-input-form">
        <div className="input-wrapper">
          <textarea
            ref={textareaRef}
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder={getPlaceholderText()}
            disabled={isDisabled}
            className="chat-textarea"
            rows={1}
            maxLength={2000}
            aria-label="Type your writing question"
          />
          <button
            type="submit"
            disabled={!message.trim() || isDisabled}
            className="send-button"
            title="Send message (Ctrl+Enter)"
            aria-label="Send message"
          >
            <svg 
              xmlns="http://www.w3.org/2000/svg" 
              width="20" 
              height="20" 
              viewBox="0 0 24 24" 
              fill="none" 
              stroke="currentColor" 
              strokeWidth="2" 
              strokeLinecap="round" 
              strokeLinejoin="round"
            >
              <line x1="22" y1="2" x2="11" y2="13"></line>
              <polygon points="22,2 15,22 11,13 2,9"></polygon>
            </svg>
          </button>
        </div>
        
        {/* Character count and keyboard hint */}
        <div className="input-footer">
          <span className="input-helper-text">
            {getInputHelperText()}
          </span>
          <span className="character-count">
            {message.length}/2000
          </span>
        </div>
      </form>
    </div>
  );
}; 