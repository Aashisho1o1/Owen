import React, { useRef, useEffect } from 'react';
import { EnhancedChatMessage } from './EnhancedChatMessage';
import { HighlightedTextDisplay } from './HighlightedTextDisplay';
import { ErrorDisplay } from './ErrorDisplay';
import { StreamingMessage } from './StreamingMessage';
import { UnhighlightButton } from './UnhighlightButton';
import { ChatMessage as ChatMessageType } from '../../services/api';
import { SuggestionOption } from '../../services/api/types';

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
  currentSuggestions?: SuggestionOption[];
  clearSuggestions?: () => void;
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
  onTestConnection,
  currentSuggestions = [],
  clearSuggestions
}) => {
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom when messages change
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, streamText]);

  return (
    <div className="messages-container">
      {/* Show highlighted text at top only if no messages yet */}
      {messages.length === 0 && (
        <HighlightedTextDisplay
          highlightedText={highlightedText || ''}
          contextualPrompts={contextualPrompts}
          onPromptClick={onPromptClick}
        />
      )}
      
      {/* Unhighlight Button - appears when text is highlighted */}
      <UnhighlightButton className="unhighlight-in-chat" />
      
      {/* Error Display */}
      <ErrorDisplay
        chatApiError={chatApiError}
        apiGlobalError={apiGlobalError}
        onTestConnection={onTestConnection}
      />
      
      {/* Chat Messages with inline highlighted text */}
      {messages.map((msg, index) => {
        // Show highlighted text before the first user message that contains highlighted text
        const showHighlightedTextBefore = highlightedText && 
          msg.role === 'user' && 
          msg.content.includes(highlightedText) &&
          !messages.slice(0, index).some(prevMsg => 
            prevMsg.role === 'user' && prevMsg.content.includes(highlightedText)
          );
        
        // Show suggestions on the last AI message if we have suggestions
        const isLastAIMessage = msg.role === 'assistant' && 
          index === messages.length - 1 && 
          Array.isArray(currentSuggestions) && currentSuggestions.length > 0;
        
        return (
          <React.Fragment key={index}>
            {/* Show highlighted text inline before relevant user message */}
            {showHighlightedTextBefore && (
              <div className="inline-highlighted-text">
                <HighlightedTextDisplay
                  highlightedText={highlightedText}
                  contextualPrompts={contextualPrompts}
                  onPromptClick={onPromptClick}
                />
              </div>
            )}
            
            <EnhancedChatMessage 
              message={msg}
              suggestions={isLastAIMessage ? currentSuggestions : []}
              originalText={highlightedText || ''}
              showSuggestions={isLastAIMessage}
            />
          </React.Fragment>
        );
      })}
      
      {/* Streaming Message */}
      <StreamingMessage
        streamText={streamText || ''}
        isStreaming={isStreaming}
      />
      
      <div ref={messagesEndRef} />
    </div>
  );
}; 
 