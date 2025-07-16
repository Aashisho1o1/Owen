import React, { useRef, useEffect } from 'react';
import { EnhancedChatMessage } from './EnhancedChatMessage';
import { HighlightedTextDisplay } from './HighlightedTextDisplay';
import { ErrorDisplay } from './ErrorDisplay';
import { UnhighlightButton } from './UnhighlightButton';
import { ChatMessage as ChatMessageType } from '../../services/api';
import { SuggestionOption } from '../../services/api/types';

interface MessagesContainerProps {
  messages: ChatMessageType[];
  highlightedText?: string;
  highlightedTextMessageIndex?: number | null;
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
  highlightedTextMessageIndex,
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
      {/* Show highlighted text at top if no messages yet OR if we have highlighted text but no user messages yet */}
      {((messages.length === 0) || 
        (highlightedText && highlightedText.trim() && !messages.some(msg => msg.role === 'user'))) && 
        highlightedText && highlightedText.trim() && (
        <HighlightedTextDisplay
          highlightedText={highlightedText}
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
        // FIXED: Show highlighted text before the specific message it's associated with
        const showHighlightedTextBefore = highlightedText && 
          highlightedText.trim() && 
          highlightedTextMessageIndex === index;
        
        // Show suggestions on the last AI message if we have suggestions
        const isLastAIMessage = msg.role === 'assistant' && 
          index === messages.length - 1 && 
          Array.isArray(currentSuggestions) && currentSuggestions.length > 0;
        
        // FIXED: Handle streaming for the last assistant message
        const isStreamingMessage = msg.role === 'assistant' && 
          index === messages.length - 1 && 
          isStreaming;
        
        // Create a modified message for streaming display
        const displayMessage = isStreamingMessage && streamText ? 
          { ...msg, content: streamText } : msg;
        
        return (
          <React.Fragment key={index}>
            {/* Show highlighted text inline before the specific associated message */}
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
              message={displayMessage}
              suggestions={isLastAIMessage ? currentSuggestions : []}
              originalText={highlightedText || ''}
              showSuggestions={isLastAIMessage}
              isStreaming={isStreamingMessage}
            />
          </React.Fragment>
        );
      })}
      
      <div ref={messagesEndRef} />
    </div>
  );
}; 
 