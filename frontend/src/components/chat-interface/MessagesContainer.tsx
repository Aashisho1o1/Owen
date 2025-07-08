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
      {/* Highlighted Text Display with Unhighlight Button */}
      <HighlightedTextDisplay
        highlightedText={highlightedText || ''}
        contextualPrompts={contextualPrompts}
        onPromptClick={onPromptClick}
      />
      
      {/* Unhighlight Button - appears when text is highlighted */}
      <UnhighlightButton className="unhighlight-in-chat" />
      
      {/* Error Display */}
      <ErrorDisplay
        chatApiError={chatApiError}
        apiGlobalError={apiGlobalError}
        onTestConnection={onTestConnection}
      />
      
      {/* Chat Messages */}
      {messages.map((msg, index) => {
        // Show suggestions on the last AI message if we have suggestions
        const isLastAIMessage = msg.role === 'assistant' && 
          index === messages.length - 1 && 
          Array.isArray(currentSuggestions) && currentSuggestions.length > 0;
        
        // Debug logging
        if (index === messages.length - 1 && msg.role === 'assistant') {
          console.log('🔍 MessagesContainer: Last AI message check:', {
            messageIndex: index,
            totalMessages: messages.length,
            messageRole: msg.role,
            currentSuggestionsCount: currentSuggestions?.length || 0,
            isLastAIMessage,
            suggestions: currentSuggestions
          });
        }
        
        return (
          <EnhancedChatMessage 
            key={index} 
            message={msg}
            suggestions={isLastAIMessage ? currentSuggestions : []}
            originalText={highlightedText || ''}
            showSuggestions={isLastAIMessage}
          />
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
 