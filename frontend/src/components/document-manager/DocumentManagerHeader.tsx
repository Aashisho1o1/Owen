import React from 'react';

interface DocumentManagerHeaderProps {
  documentCount: number;
  totalWordCount: number;
  onClose: () => void;
  onReturnToWriting?: () => void; // New prop for returning to writing space
}

/**
 * Molecular component: Document Manager Header
 * Single Responsibility: Display header with stats, navigation, and close button
 */
export const DocumentManagerHeader: React.FC<DocumentManagerHeaderProps> = ({
  documentCount,
  totalWordCount,
  onClose,
  onReturnToWriting
}) => {
  return (
    <div className="document-manager-header">
      <h2>📄 Document Manager</h2>
      <div className="header-actions">
        <div className="total-stats">
          {documentCount} documents • {totalWordCount.toLocaleString()} words
        </div>
        <div className="header-buttons">
          {onReturnToWriting && (
            <button 
              onClick={onReturnToWriting} 
              className="control-button"
              title="Return to Writing Space"
            >
              ✏️ Writing
            </button>
          )}
          <button onClick={onClose} className="close-button">
            ✕
          </button>
        </div>
      </div>
    </div>
  );
}; 
 