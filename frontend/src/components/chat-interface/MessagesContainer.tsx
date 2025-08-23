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
  currentSuggestions = []
}) => {
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const { premiumStatus } = useChatContext();
  
  // Track if highlighted text has been shown to prevent duplicate display
  const [shownHighlightedTextIndex, setShownHighlightedTextIndex] = useState<number | null>(null);
  const [lastHighlightedText, setLastHighlightedText] = useState<string>('');
  
  // Smart auto-scroll state - only scroll when user is near bottom
  const [autoScrollEnabled, setAutoScrollEnabled] = useState(true);
  
  // NEW: Toggle state for highlighted section (Behavioral Psychology: User Control)
  const [showHighlightedSection, setShowHighlightedSection] = useState(true);

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
        <>
          {/* Toggle Button - Behavioral Psychology: Progressive Disclosure */}
          <button 
            onClick={() => setShowHighlightedSection(!showHighlightedSection)}
            className="highlight-section-toggle"
            aria-expanded={showHighlightedSection}
            aria-label={showHighlightedSection ? 'Hide highlighted section' : 'Show highlighted section'}
          >
            <span className="toggle-icon">{showHighlightedSection ? '📖' : '📝'}</span>
            <span className="toggle-text">
              {showHighlightedSection ? 'Hide Context' : `Show Context: "${highlightedText.substring(0, 40)}..."`}
            </span>
            <span className="toggle-arrow">{showHighlightedSection ? '▼' : '▶'}</span>
          </button>
          
          {/* Collapsible Highlighted Section */}
          {showHighlightedSection && (
            <HighlightedTextDisplay
              highlightedText={highlightedText}
              contextualPrompts={contextualPrompts}
              onPromptClick={onPromptClick}
            />
          )}
        </>
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
            {/* Context Badge - Cursor-inspired minimal design */}
            {messageHasHighlightedText && msg.role === 'user' && (
              <div className="message-context-badge">
                <span className="context-icon">📝</span>
                <span className="context-preview">
                  Context: "{msg.highlightedText!.substring(0, 30)}..."
                </span>
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
        
        /* NEW: Highlight Section Toggle Button */
        .highlight-section-toggle {
          display: flex;
          align-items: center;
          gap: 8px;
          width: 100%;
          padding: 10px 16px;
          margin-bottom: 12px;
          background: rgba(59, 130, 246, 0.05);
          border: 1px solid rgba(59, 130, 246, 0.2);
          border-radius: 8px;
          color: #3b82f6;
          font-size: 13px;
          font-weight: 500;
          cursor: pointer;
          transition: all 0.2s ease;
        }
        
        .highlight-section-toggle:hover {
          background: rgba(59, 130, 246, 0.1);
          border-color: rgba(59, 130, 246, 0.3);
          transform: translateY(-1px);
        }
        
        .toggle-icon {
          font-size: 16px;
          flex-shrink: 0;
        }
        
        .toggle-text {
          flex: 1;
          text-align: left;
          overflow: hidden;
          text-overflow: ellipsis;
          white-space: nowrap;
        }
        
        .toggle-arrow {
          font-size: 12px;
          flex-shrink: 0;
          transition: transform 0.2s ease;
        }
        
        /* NEW: Message Context Badge */
        .message-context-badge {
          display: inline-flex;
          align-items: center;
          gap: 6px;
          padding: 4px 10px;
          margin-bottom: 8px;
          background: rgba(156, 163, 175, 0.08);
          border: 1px solid rgba(156, 163, 175, 0.15);
          border-radius: 16px;
          color: #6b7280;
          font-size: 11px;
          font-weight: 500;
        }
        
        .context-icon {
          font-size: 12px;
          opacity: 0.8;
        }
        
        .context-preview {
          font-style: italic;
          opacity: 0.9;
          max-width: 300px;
          overflow: hidden;
          text-overflow: ellipsis;
          white-space: nowrap;
        }
        
        @media (max-width: 768px) {
          .premium-status-bar {
            padding: 6px 12px;
          }
          
          .status-message {
            font-size: 0.75rem;
          }
          
          .highlight-section-toggle {
            padding: 8px 12px;
            font-size: 12px;
          }
          
          .message-context-badge {
            font-size: 10px;
            padding: 3px 8px;
          }
          
          .context-preview {
            max-width: 200px;
          }
        }
      `}</style>
    </div>
  );
}; 
 