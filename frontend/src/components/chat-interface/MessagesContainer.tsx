import React, { useRef, useEffect } from 'react';
import { ChatMessage } from '../chat/ChatMessage';
import { HighlightedTextDisplay } from './HighlightedTextDisplay';
import { ErrorDisplay } from './ErrorDisplay';
import { StreamingMessage } from './StreamingMessage';
import { ChatMessage as ChatMessageType } from '../../services/api';

interface MessagesContainerProps {
  messages: ChatMessageType[];
  highlightedText?: string;
  contextualPrompts: string[];
  chatApiError?: string | null;
  apiGlobalError?: string | null;
  streamText?: string;
  isStreaming: boolean;
  onPromptClick: (prompt: string) => void;
  onTestConnection: () => Promise<void>;
}

/**
 * Organism Component: Messages Container
 * Single Responsibility: Orchestrate all message-related displays and auto-scroll
 */
export const MessagesContainer: React.FC<MessagesContainerProps> = ({
  messages,
  highlightedText,
  contextualPrompts,
  chatApiError,
  apiGlobalError,
  streamText,
  isStreaming,
  onPromptClick,
  onTestConnection
}) => {
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom when messages change
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, streamText]);

  return (
    <div className="messages-container">
      {/* Highlighted Text Display */}
      <HighlightedTextDisplay
        highlightedText={highlightedText || ''}
        contextualPrompts={contextualPrompts}
        onPromptClick={onPromptClick}
      />
      
      {/* Error Display */}
      <ErrorDisplay
        chatApiError={chatApiError}
        apiGlobalError={apiGlobalError}
        onTestConnection={onTestConnection}
      />
      
      {/* Chat Messages */}
      {messages.map((msg, index) => (
        <ChatMessage 
          key={index} 
          message={msg}
        />
      ))}
      
      {/* Streaming Message */}
      <StreamingMessage
        streamText={streamText || ''}
        isStreaming={isStreaming}
      />
      
      <div ref={messagesEndRef} />
    </div>
  );
}; 
 