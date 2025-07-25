/**
 * EnhancedChatMessage Component
 * 
 * Displays chat messages with optional suggestions that users can accept.
 * Integrates with the new AI suggestions feature.
 */

import React from 'react';
import { ChatMessage, SuggestionOption } from '../../services/api/types';
import { SuggestionsDisplay } from './SuggestionsDisplay';
import { useChatContext } from '../../contexts/ChatContext';
import { useEditorContext } from '../../contexts/EditorContext';

interface EnhancedChatMessageProps {
  message: ChatMessage;
  suggestions?: SuggestionOption[];
  originalText?: string;
  showSuggestions?: boolean;
  isStreaming?: boolean;
}

export const EnhancedChatMessage: React.FC<EnhancedChatMessageProps> = ({
  message,
  suggestions = [],
  originalText = '',
  showSuggestions = false,
  isStreaming = false
}) => {
  const { 
    acceptTextSuggestion, 
    isAcceptingSuggestion, 
    acceptedSuggestionId 
  } = useChatContext();
  
  const { setEditorContent } = useEditorContext();

  // SECURE HTML entity decoder function - prevents XSS attacks
  const decodeHtmlEntities = (text: string): string => {
    // Safe HTML entity decoding using replace with predefined entities
    const entityMap: { [key: string]: string } = {
      '&amp;': '&',
      '&lt;': '<',
      '&gt;': '>',
      '&quot;': '"',
      '&#39;': "'",
      '&#x27;': "'",
      '&#x2F;': '/',
      '&#x60;': '`',
      '&#x3D;': '='
    };
    
    return text.replace(/&(?:amp|lt|gt|quot|#39|#x27|#x2F|#x60|#x3D);/g, (entity) => {
      return entityMap[entity] || entity;
    });
  };

  const renderTextWithLineBreaks = (text: string) => {
    return text.split('\n').map((line, index) => (
      <React.Fragment key={index}>
        {line}
        {index < text.split('\n').length - 1 && <br />}
      </React.Fragment>
    ));
  };

  const renderCodeBlocks = (text: string) => {
    const parts = text.split('```');
    return parts.map((part, index) => {
      if (index % 2 === 1) {
        // This is a code block
        return (
          <pre key={index} className="code-block">
            <code>{part.trim()}</code>
          </pre>
        );
      } else {
        // Regular text
        return <span key={index}>{renderTextWithLineBreaks(part)}</span>;
      }
    });
  };

  const renderBoldText = (text: string) => {
    const parts = text.split('**');
    return parts.map((part, index) => {
      if (index % 2 === 1) {
        return <strong key={index}>{part}</strong>;
      } else {
        return <span key={index}>{renderTextWithLineBreaks(part)}</span>;
      }
    });
  };

  const renderBulletPoints = (text: string) => {
    const lines = text.split('\n');
    const result: React.ReactNode[] = [];
    let currentList: string[] = [];
    
    lines.forEach((line, index) => {
      if (line.trim().startsWith('•') || line.trim().startsWith('-')) {
        currentList.push(line.trim().substring(1).trim());
      } else {
        if (currentList.length > 0) {
          result.push(
            <ul key={`list-${index}`} className="bullet-list">
              {currentList.map((item, i) => (
                <li key={i}>{item}</li>
              ))}
            </ul>
          );
          currentList = [];
        }
        if (line.trim()) {
          result.push(<p key={index}>{line}</p>);
        }
      }
    });
    
    // Handle remaining list items
    if (currentList.length > 0) {
      result.push(
        <ul key="final-list" className="bullet-list">
          {currentList.map((item, i) => (
            <li key={i}>{item}</li>
          ))}
        </ul>
      );
    }
    
    return result;
  };

  const renderMessageContent = (msg: ChatMessage) => {
    // Decode HTML entities first
    const content = decodeHtmlEntities(msg.content);
    
    if (msg.role === 'user') {
      return renderTextWithLineBreaks(content);
    }

    // AI message formatting with markdown-like syntax
    // Handle code blocks
    if (content.includes('```')) {
      return renderCodeBlocks(content);
    }
    
    // Handle bold text
    if (content.includes('**')) {
      return renderBoldText(content);
    }
    
    // Handle bullet points
    if (content.includes('•') || content.includes('-')) {
      return renderBulletPoints(content);
    }
    
    return renderTextWithLineBreaks(content);
  };

  const handleAcceptSuggestion = async (suggestion: SuggestionOption) => {
    try {
      await acceptTextSuggestion(suggestion, (newContent, replacementInfo) => {
        console.log('📝 Content updated via suggestion:', {
          newContentLength: newContent.length,
          replacementInfo
        });
        setEditorContent(newContent);
      });
    } catch (error) {
      console.error('❌ Failed to accept suggestion:', error);
    }
  };

  // Determine message styling based on role and streaming state
  const messageClass = `message ${message.role}-message${isStreaming ? ' streaming' : ''}`;

  return (
    <div className={messageClass}>
      <div className="message-avatar">
        {message.role === 'user' ? (
          <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path>
            <circle cx="12" cy="7" r="4"></circle>
          </svg>
        ) : (
          <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <rect x="3" y="4" width="18" height="18" rx="2" ry="2"></rect>
            <line x1="16" y1="2" x2="16" y2="6"></line>
            <line x1="8" y1="2" x2="8" y2="6"></line>
            <line x1="3" y1="10" x2="21" y2="10"></line>
          </svg>
        )}
      </div>
      <div className="message-content">
        {renderMessageContent(message)}
        {/* Add typing cursor only for streaming AI messages */}
        {isStreaming && message.role === 'assistant' && (
          <span className="typing-cursor" aria-hidden="true">|</span>
        )}
      </div>
      
      {/* Show suggestions for AI messages when available */}
      {showSuggestions && suggestions.length > 0 && (
        <SuggestionsDisplay
          suggestions={suggestions}
          originalText={originalText}
          onAcceptSuggestion={handleAcceptSuggestion}
          isAccepting={isAcceptingSuggestion}
          acceptedSuggestionId={acceptedSuggestionId || undefined}
        />
      )}
    </div>
  );
};

export default EnhancedChatMessage; 