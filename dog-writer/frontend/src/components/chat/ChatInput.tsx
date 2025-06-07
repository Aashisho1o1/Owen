/**
 * ChatInput Component
 * 
 * Handles user input for chat messages with keyboard shortcuts,
 * suggested questions, and proper form validation.
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
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // Auto-resize textarea
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${textareaRef.current.scrollHeight}px`;
    }
  }, [message]);

  // Focus textarea when component mounts
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
    }
  };

  return (
    <div className="chat-input-container">
      {/* Suggested Questions */}
      {suggestedQuestions.length > 0 && highlightedText && (
        <div className="suggested-questions">
          <div className="suggested-questions-title">Suggested questions:</div>
          <div className="suggested-questions-list">
            {suggestedQuestions.map((question, index) => (
              <button
                key={index}
                className="suggested-question-button"
                onClick={() => handleSuggestedQuestion(question)}
                disabled={isDisabled}
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
            placeholder={
              highlightedText 
                ? "Ask about the selected text..." 
                : "Type your message here..."
            }
            disabled={isDisabled}
            className="chat-textarea"
            rows={1}
            maxLength={2000}
          />
          <button
            type="submit"
            disabled={!message.trim() || isDisabled}
            className="send-button"
            title="Send message (Ctrl+Enter)"
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
          <span className="character-count">
            {message.length}/2000
          </span>
          <span className="keyboard-hint">
            Press Ctrl+Enter to send
          </span>
        </div>
      </form>
    </div>
  );
}; 