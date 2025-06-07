/**
 * ThinkingTrail Component
 * 
 * Displays the AI's thinking process with expandable/collapsible sections
 * and proper formatting for better user understanding.
 */

import React, { useState } from 'react';

interface ThinkingTrailProps {
  trail?: string;
  isThinking?: boolean;
  isVisible?: boolean;
  onToggleVisibility?: () => void;
}

export const ThinkingTrail: React.FC<ThinkingTrailProps> = ({ 
  trail, 
  isThinking = false, 
  isVisible = false,
  onToggleVisibility 
}) => {
  const [isExpanded, setIsExpanded] = useState(false);

  if (!trail && !isThinking) {
    return null;
  }

  const formatThinkingTrail = (text: string) => {
    // Split by common thinking patterns
    const sections = text.split(/(?=\*\*[A-Z][^*]*\*\*)/);
    
    return sections.map((section, index) => {
      if (section.trim().startsWith('**') && section.includes('**')) {
        // This is a header section
        const headerMatch = section.match(/\*\*(.*?)\*\*/);
        const header = headerMatch ? headerMatch[1] : '';
        const content = section.replace(/\*\*.*?\*\*/, '').trim();
        
        return (
          <div key={index} className="thinking-section">
            <div className="thinking-header">{header}</div>
            {content && (
              <div className="thinking-content">
                {content.split('\n').map((line, lineIndex) => (
                  <p key={lineIndex}>{line}</p>
                ))}
              </div>
            )}
          </div>
        );
      } else if (section.trim()) {
        // Regular content
        return (
          <div key={index} className="thinking-content">
            {section.split('\n').map((line, lineIndex) => (
              <p key={lineIndex}>{line}</p>
            ))}
          </div>
        );
      }
      return null;
    }).filter(Boolean);
  };

  return (
    <div className="thinking-trail-container">
      {/* Toggle Button */}
      {onToggleVisibility && (
        <button 
          className="thinking-trail-toggle"
          onClick={onToggleVisibility}
          title={isVisible ? 'Hide AI thinking process' : 'Show AI thinking process'}
        >
          <svg 
            xmlns="http://www.w3.org/2000/svg" 
            width="16" 
            height="16" 
            viewBox="0 0 24 24" 
            fill="none" 
            stroke="currentColor" 
            strokeWidth="2" 
            strokeLinecap="round" 
            strokeLinejoin="round"
            className={isVisible ? 'rotated' : ''}
          >
            <polyline points="6,9 12,15 18,9"></polyline>
          </svg>
          {isVisible ? 'Hide' : 'Show'} AI Thinking
        </button>
      )}

      {/* Thinking Trail Content */}
      {isVisible && (
        <div className="thinking-trail-content">
          {isThinking && (
            <div className="thinking-indicator">
              <div className="thinking-dots">
                <span></span>
                <span></span>
                <span></span>
              </div>
              <span className="thinking-text">AI is thinking...</span>
            </div>
          )}

          {trail && (
            <div className="thinking-trail">
              <div className="thinking-trail-header">
                <h4>AI Thinking Process</h4>
                <button
                  className="expand-collapse-button"
                  onClick={() => setIsExpanded(!isExpanded)}
                >
                  {isExpanded ? 'Collapse' : 'Expand'}
                </button>
              </div>
              
              <div className={`thinking-trail-body ${isExpanded ? 'expanded' : 'collapsed'}`}>
                {formatThinkingTrail(trail)}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}; 