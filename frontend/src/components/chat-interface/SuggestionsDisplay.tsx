/**
 * SuggestionsDisplay Component
 * 
 * Displays multiple AI suggestions with accept buttons.
 * Handles the visual presentation of suggestions and acceptance UI.
 * 
 * Features:
 * - Multiple suggestion options with confidence indicators
 * - Accept buttons with clear visual feedback
 * - Hover states and smooth animations
 * - Explanations for each suggestion
 * - Responsive design
 */

import React, { useState } from 'react';
import { SuggestionOption } from '../../services/api/types';
import './SuggestionsDisplay.css';

interface SuggestionsDisplayProps {
  suggestions: SuggestionOption[];
  originalText: string;
  onAcceptSuggestion: (suggestion: SuggestionOption) => void;
  isAccepting?: boolean;
  acceptedSuggestionId?: string;
}

export const SuggestionsDisplay: React.FC<SuggestionsDisplayProps> = ({
  suggestions,
  originalText,
  onAcceptSuggestion,
  isAccepting = false,
  acceptedSuggestionId
}) => {
  const [hoveredSuggestion, setHoveredSuggestion] = useState<string | null>(null);

  const getSuggestionTypeIcon = (type: string): string => {
    switch (type.toLowerCase()) {
      case 'clarity_improvement':
        return '🔍';
      case 'style_enhancement':
        return '✨';
      case 'conciseness':
        return '🎯';
      case 'grammar_fix':
        return '📝';
      case 'tone_adjustment':
        return '🎨';
      default:
        return '💡';
    }
  };

  const getConfidenceColor = (confidence: number): string => {
    if (confidence >= 0.9) return '#10b981'; // Green
    if (confidence >= 0.8) return '#f59e0b'; // Yellow
    return '#6b7280'; // Gray
  };

  const formatSuggestionType = (type: string): string => {
    return type.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
  };

  if (!suggestions || suggestions.length === 0) {
    return null;
  }

  return (
    <div className="suggestions-display">
      <div className="suggestions-header">
        <h4>✨ Suggested Improvements</h4>
        <span className="original-text-preview">
          "{originalText.length > 60 ? originalText.substring(0, 60) + '...' : originalText}"
        </span>
      </div>

      <div className="suggestions-list">
        {suggestions.map((suggestion) => (
          <div
            key={suggestion.id}
            className={`suggestion-item ${hoveredSuggestion === suggestion.id ? 'hovered' : ''} ${
              acceptedSuggestionId === suggestion.id ? 'accepted' : ''
            }`}
            onMouseEnter={() => setHoveredSuggestion(suggestion.id)}
            onMouseLeave={() => setHoveredSuggestion(null)}
          >
            <div className="suggestion-header">
              <div className="suggestion-meta">
                <span className="suggestion-icon">
                  {getSuggestionTypeIcon(suggestion.type)}
                </span>
                <span className="suggestion-type">
                  {formatSuggestionType(suggestion.type)}
                </span>
                <div className="confidence-indicator">
                  <div 
                    className="confidence-bar"
                    style={{ 
                      width: `${suggestion.confidence * 100}%`,
                      backgroundColor: getConfidenceColor(suggestion.confidence)
                    }}
                  />
                  <span className="confidence-text">
                    {Math.round(suggestion.confidence * 100)}%
                  </span>
                </div>
              </div>
              
              <button
                className={`accept-button ${
                  isAccepting && acceptedSuggestionId === suggestion.id ? 'accepting' : ''
                }`}
                onClick={() => onAcceptSuggestion(suggestion)}
                disabled={isAccepting}
                title="Accept this suggestion"
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '6px',
                  padding: '8px 16px',
                  background: '#14b8a6',
                  color: 'white',
                  border: '2px solid #14b8a6',
                  borderRadius: '6px',
                  fontSize: '14px',
                  fontWeight: '600',
                  cursor: 'pointer',
                  minWidth: '80px',
                  justifyContent: 'center',
                  boxShadow: '0 2px 4px rgba(0, 0, 0, 0.1)',
                  position: 'relative',
                  zIndex: 10,
                  opacity: 1,
                  visibility: 'visible'
                }}
              >
                {isAccepting && acceptedSuggestionId === suggestion.id ? (
                  <span className="accepting-spinner" style={{ color: 'white' }}>⏳</span>
                ) : (
                  <span className="accept-icon" style={{ color: 'white', fontSize: '16px', fontWeight: 'bold' }}>✓</span>
                )}
                <span style={{ color: 'white', fontWeight: '600' }}>Accept</span>
              </button>
            </div>

            <div className="suggestion-content">
              <div className="suggested-text">
                {suggestion.text}
              </div>
              
              {suggestion.explanation && (
                <div className="suggestion-explanation">
                  <span className="explanation-icon">💭</span>
                  {suggestion.explanation}
                </div>
              )}
            </div>

            <div className="suggestion-footer">
              <div className="text-comparison">
                <span className="comparison-label">Length:</span>
                <span className={`length-change ${
                  suggestion.text.length > originalText.length ? 'longer' : 
                  suggestion.text.length < originalText.length ? 'shorter' : 'same'
                }`}>
                  {suggestion.text.length > originalText.length ? '+' : ''}
                  {suggestion.text.length - originalText.length} chars
                </span>
              </div>
            </div>
          </div>
        ))}
      </div>

      <div className="suggestions-footer">
        <p className="suggestions-hint">
          💡 <strong>Tip:</strong> Click "Accept" to replace your selected text with any of these options. 
          The new text will be underlined so you can easily identify and edit it further.
        </p>
      </div>
    </div>
  );
};

export default SuggestionsDisplay; 