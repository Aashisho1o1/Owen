import React from 'react';

interface HighlightTooltipProps {
  isVisible: boolean;
  position: { x: number; y: number };
  selectedText: string;
  onCreateHighlight: (color: string, requestType: string) => void;
  onCancel: () => void;
}

/**
 * Molecular Component: Highlight Tooltip
 * Single Responsibility: Display highlighting options when text is selected
 */
export const HighlightTooltip: React.FC<HighlightTooltipProps> = ({
  isVisible,
  position,
  selectedText,
  onCreateHighlight,
  onCancel
}) => {
  if (!isVisible) return null;

  const truncatedText = selectedText.length > 50 
    ? selectedText.substring(0, 50) + '...' 
    : selectedText;

  return (
    <div 
      className="highlight-tooltip"
      style={{
        position: 'fixed',
        left: `${position.x}px`,
        top: `${position.y}px`,
        zIndex: 1000,
      }}
    >
      <div className="highlight-tooltip-content">
        <div className="highlight-tooltip-text">
          Get AI feedback on: "{truncatedText}"
        </div>
        <div className="highlight-tooltip-actions">
          <button
            className="highlight-btn highlight-btn-primary"
            onClick={() => onCreateHighlight('feedback-request', 'feedback')}
          >
            🔍 Get Feedback
          </button>
          <button
            className="highlight-btn highlight-btn-secondary"
            onClick={() => onCreateHighlight('improvement', 'improve')}
          >
            ✨ Improve This
          </button>
          <button
            className="highlight-btn highlight-btn-tertiary"
            onClick={() => onCreateHighlight('question', 'question')}
          >
            ❓ Ask Question
          </button>
          <button
            className="highlight-btn highlight-btn-cancel"
            onClick={onCancel}
          >
            ✕
          </button>
        </div>
      </div>
    </div>
  );
};
