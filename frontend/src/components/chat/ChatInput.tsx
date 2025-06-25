/**
 * ChatInput Component - Enhanced Conversational Interface
 * 
 * Handles user input for chat messages with keyboard shortcuts,
 * and improved visual feedback.
 */

import React, { useState, useRef, useEffect } from 'react';

interface ChatInputProps {
  onSendMessage: (message: string) => void;
  isDisabled?: boolean;
  highlightedText?: string;
}

export const ChatInput: React.FC<ChatInputProps> = ({ 
  onSendMessage, 
  isDisabled = false, 
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
    return ""; // Clean minimal interface
  };

  return (
    <div className="chat-input-container">
      {/* Suggested Questions - REMOVED COMPLETELY as requested by user */}
      {/* They are redundant since highlighted text already provides contextual suggestions */}

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