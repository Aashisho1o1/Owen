import React, { useRef, useEffect, useState } from 'react';
import { EnhancedChatMessage } from './EnhancedChatMessage';
import { HighlightedTextDisplay } from './HighlightedTextDisplay';
import { ErrorDisplay } from './ErrorDisplay';
import { UnhighlightButton } from './UnhighlightButton';
import { ChatMessage as ChatMessageType } from '../../services/api';
import { SuggestionOption } from '../../services/api/types';
import { useChatContext } from '../../contexts/ChatContext';

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
 * Single Responsibility: Orchestrate all message-related displays and smart auto-scroll
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
  const containerRef = useRef<HTMLDivElement>(null);
  const { premiumStatus } = useChatContext();
  
  // Track if highlighted text has been shown to prevent duplicate display
  const [shownHighlightedTextIndex, setShownHighlightedTextIndex] = useState<number | null>(null);
  const [lastHighlightedText, setLastHighlightedText] = useState<string>('');
  
  // Smart auto-scroll state - only scroll when user is near bottom
  const [autoScrollEnabled, setAutoScrollEnabled] = useState(true);

  // Handle user scroll to detect if they want auto-scroll or not
  const handleUserScroll = () => {
    if (!containerRef.current) return;
    const { scrollTop, scrollHeight, clientHeight } = containerRef.current;
    // Within 60px of bottom = user wants to see new messages
    const distanceFromBottom = scrollHeight - (scrollTop + clientHeight);
    setAutoScrollEnabled(distanceFromBottom < 60);
  };

  // Set up scroll listener
  useEffect(() => {
    const container = containerRef.current;
    if (!container) return;
    
    container.addEventListener('scroll', handleUserScroll);
    return () => container.removeEventListener('scroll', handleUserScroll);
  }, []);

  // Smart auto-scroll - only when user wants it
  useEffect(() => {
    if (autoScrollEnabled) {
      messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }
  }, [messages, streamText, autoScrollEnabled]);
  
  // Reset shown highlighted text when the actual highlighted text changes (not just the index)
  useEffect(() => {
    if (highlightedText !== lastHighlightedText) {
      setShownHighlightedTextIndex(null);
      setLastHighlightedText(highlightedText || '');
    }
  }, [highlightedText, lastHighlightedText]);

  return (
    <div ref={containerRef} className="messages-container">
      {/* Premium Status Messages */}
      {(premiumStatus.folderScope || premiumStatus.voiceGuard) && (
        <div className="premium-status-bar">
          {premiumStatus.folderScope && (
            <div className="status-message folder-scope">
              {premiumStatus.folderScope}
            </div>
          )}
          {premiumStatus.voiceGuard && (
            <div className="status-message voice-guard">
              {premiumStatus.voiceGuard}
            </div>
          )}
        </div>
      )}

      {/* Display an inline preview of the currently selected text
          as soon as the user clicks "Ask AI". It remains visible
          until the first related question is asked, after which it
          gets anchored to that message via highlightedTextMessageIndex. */}
      {highlightedText && highlightedText.trim() && highlightedTextMessageIndex === null && (
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
        // Check if this message should show current active highlighted text
        const shouldShowCurrentHighlight = (
          highlightedText &&
          highlightedText.trim() &&
          highlightedTextMessageIndex === index &&
          shownHighlightedTextIndex !== index
        );

        // Check if this specific message has preserved highlighted text
        const messageHasHighlightedText = msg.highlightedText && msg.highlightedText.trim();
        
        // Check if this is the last AI message for suggestions
        const isLastAIMessage = msg.role === 'assistant' && index === messages.length - 1;
        
        // Mark that we've shown this highlighted text
        if (shouldShowCurrentHighlight && shownHighlightedTextIndex !== index) {
          setShownHighlightedTextIndex(index);
        }

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
            
            {/* The actual message with streaming support built-in */}
            <EnhancedChatMessage
              message={msg}
              suggestions={isLastAIMessage ? currentSuggestions : []}
              showSuggestions={isLastAIMessage}
              isStreaming={isStreaming && isLastAIMessage}
            />
          </div>
        );
      })}
      
      {/* REMOVED: Duplicate streaming message that was causing empty boxes */}
      {/* The streaming effect is now handled within EnhancedChatMessage */}
      
      <div ref={messagesEndRef} />
      
      <style>{`
        .premium-status-bar {
          position: sticky;
          top: 0;
          z-index: 10;
          padding: 8px 16px;
          background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
          border-bottom: 1px solid #bae6fd;
          margin-bottom: 8px;
        }
        
        .status-message {
          font-size: 0.8125rem;
          font-weight: 500;
          color: #0369a1;
          display: flex;
          align-items: center;
          gap: 6px;
          margin-bottom: 4px;
        }
        
        .status-message:last-child {
          margin-bottom: 0;
        }
        
        .status-message.folder-scope {
          color: #059669;
        }
        
        .status-message.voice-guard {
          color: #7c3aed;
        }
        
        @media (max-width: 768px) {
          .premium-status-bar {
            padding: 6px 12px;
          }
          
          .status-message {
            font-size: 0.75rem;
          }
        }
      `}</style>
    </div>
  );
}; 
 