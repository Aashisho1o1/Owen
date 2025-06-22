import React from 'react';

interface DocumentManagerHeaderProps {
  documentCount: number;
  totalWordCount: number;
  onClose: () => void;
}

/**
 * Molecular component: Document Manager Header
 * Single Responsibility: Display header with stats and close button
 */
export const DocumentManagerHeader: React.FC<DocumentManagerHeaderProps> = ({
  documentCount,
  totalWordCount,
  onClose
}) => {
  return (
    <div className="document-manager-header">
      <h2>📄 Document Manager</h2>
      <div className="header-actions">
        <div className="total-stats">
          {documentCount} documents • {totalWordCount.toLocaleString()} words
        </div>
        <button onClick={onClose} className="close-button">
          ✕
        </button>
      </div>
    </div>
  );
}; 
 