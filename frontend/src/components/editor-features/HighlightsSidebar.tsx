import React from 'react';
import { HighlightInfo } from './CustomHighlightExtension';

interface HighlightsSidebarProps {
  highlights: HighlightInfo[];
  onRemoveHighlight: (highlightId: string) => void;
  onClearAll: () => void;
}

/**
 * Organism Component: Highlights Sidebar
 * Single Responsibility: Display and manage all highlights in a sidebar
 */
export const HighlightsSidebar: React.FC<HighlightsSidebarProps> = ({
  highlights,
  onRemoveHighlight,
  onClearAll
}) => {
  if (highlights.length === 0) return null;

  const getHighlightTypeDisplay = (color: string) => {
    switch (color) {
      case 'feedback-request': return '🔍 Feedback';
      case 'improvement': return '✨ Improve';
      case 'question': return '❓ Question';
      default: return '📝 Highlight';
    }
  };

  return (
    <div className="highlights-sidebar">
      <div className="highlights-header">
        <h3>📝 Highlighted for Feedback</h3>
        <span className="highlights-count">{highlights.length}</span>
      </div>
      <div className="highlights-list">
        {highlights.map((highlight) => (
          <div key={highlight.id} className={`highlight-item highlight-${highlight.color}`}>
            <div className="highlight-item-text">
              {highlight.text.length > 100 
                ? highlight.text.substring(0, 100) + '...' 
                : highlight.text
              }
            </div>
            <div className="highlight-item-meta">
              <span className="highlight-type">
                {getHighlightTypeDisplay(highlight.color)}
              </span>
              <button
                className="highlight-remove-btn"
                onClick={() => onRemoveHighlight(highlight.id)}
                title="Remove highlight"
              >
                ✕
              </button>
            </div>
          </div>
        ))}
      </div>
      <div className="highlights-actions">
        <button
          className="clear-all-highlights-btn"
          onClick={onClearAll}
        >
          Clear All Highlights
        </button>
      </div>
    </div>
  );
};
