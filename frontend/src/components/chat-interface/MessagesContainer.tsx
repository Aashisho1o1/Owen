import React, { useRef, useEffect, useState } from 'react';
import { EnhancedChatMessage } from './EnhancedChatMessage';
import { HighlightedTextDisplay } from './HighlightedTextDisplay';
import { ErrorDisplay } from './ErrorDisplay';
import { UnhighlightButton } from './UnhighlightButton';
import { ChatMessage as ChatMessageType } from '../../services/api';
import { SuggestionOption } from '../../services/api/types';
import { StreamingMessage } from './StreamingMessage';

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
  
  // Track if highlighted text has been shown to prevent duplicate display
  const [shownHighlightedTextIndex, setShownHighlightedTextIndex] = useState<number | null>(null);
  const [lastHighlightedText, setLastHighlightedText] = useState<string>('');

  // Auto-scroll to bottom when messages change
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, streamText]);
  
  // Reset shown highlighted text when the actual highlighted text changes (not just the index)
  useEffect(() => {
    if (highlightedText !== lastHighlightedText) {
      setShownHighlightedTextIndex(null);
      setLastHighlightedText(highlightedText || '');
    }
  }, [highlightedText, lastHighlightedText]);

  return (
    <div className="messages-container">
      {/* Display an inline preview of the currently selected text
          as soon as the user clicks “Ask AI”. It remains visible
          until the first related question is asked, after which it
          gets anchored to that message via highlightedTextMessageIndex. */}
      {highlightedText && highlightedText.trim() && highlightedTextMessageIndex === null && messages.length === 0 && (
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
      
      {/* Chat Messages with preserved highlighted text context */}
      {messages.map((msg, index) => {
        // Show current active highlighted text at the specific message it's associated with
        const shouldShowCurrentHighlight = highlightedText && 
          highlightedText.trim() && 
          highlightedTextMessageIndex === index &&
          shownHighlightedTextIndex !== index;
        
        // Show preserved highlighted text from this message (if any)
        const messageHasHighlightedText = msg.highlightedText && msg.highlightedText.trim();
        
        // Mark as shown if we're about to show current highlight
        if (shouldShowCurrentHighlight) {
          setShownHighlightedTextIndex(index);
        }
        
        // Show suggestions on the last AI message if we have suggestions
        const isLastAIMessage = msg.role === 'assistant' && 
          index === messages.length - 1 && 
          Array.isArray(currentSuggestions) && currentSuggestions.length > 0;

        return (
          <div key={index}>
            {/* Show current active highlighted text before this message */}
            {shouldShowCurrentHighlight && (
              <div className="inline-highlighted-text">
                <HighlightedTextDisplay
                  highlightedText={highlightedText}
                  contextualPrompts={contextualPrompts}
                  onPromptClick={onPromptClick}
                />
              </div>
            )}
            
            {/* Show preserved highlighted text from this message's context */}
            {messageHasHighlightedText && msg.role === 'user' && (
              <div className="inline-highlighted-text">
                <HighlightedTextDisplay
                  highlightedText={msg.highlightedText!}
                  contextualPrompts={contextualPrompts}
                  onPromptClick={onPromptClick}
                />
              </div>
            )}
            
            {/* The actual message */}
            <EnhancedChatMessage
              message={msg}
              suggestions={isLastAIMessage ? currentSuggestions : []}
              showSuggestions={isLastAIMessage}
              isStreaming={isStreaming && index === messages.length - 1}
            />
          </div>
        );
      })}
      
      {/* Streaming message */}
      {isStreaming && streamText && (
        <StreamingMessage
          streamText={streamText}
          isStreaming={isStreaming}
        />
      )}

      {/* If a highlight is pending display (before first question) AND we already have messages above, make sure it appears just before the bottom anchor so it’s in the reader’s view. */}
      {highlightedText && highlightedText.trim() && highlightedTextMessageIndex === null && messages.length > 0 && (
        <div className="inline-highlighted-text">
          <HighlightedTextDisplay
            highlightedText={highlightedText}
            contextualPrompts={contextualPrompts}
            onPromptClick={onPromptClick}
          />
        </div>
      )}
      
      <div ref={messagesEndRef} />
    </div>
  );
}; 
 