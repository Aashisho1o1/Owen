import React from 'react';

interface StreamingMessageProps {
  streamText: string;
  isStreaming: boolean;
}

/**
 * Molecular Component: Streaming Message
 * Single Responsibility: Display streaming AI response with typing indicator
 */
export const StreamingMessage: React.FC<StreamingMessageProps> = ({
  streamText,
  isStreaming
}) => {
  if (!isStreaming || !streamText) return null;

  return (
    <div className="message ai-message streaming">
      <div className="message-avatar">
        <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <rect x="3" y="4" width="18" height="18" rx="2" ry="2"></rect>
          <line x1="16" y1="2" x2="16" y2="6"></line>
          <line x1="8" y1="2" x2="8" y2="6"></line>
          <line x1="3" y1="10" x2="21" y2="10"></line>
        </svg>
      </div>
      <div className="message-content">
        {streamText}
        <span className="typing-cursor">|</span>
      </div>
    </div>
  );
}; 
 