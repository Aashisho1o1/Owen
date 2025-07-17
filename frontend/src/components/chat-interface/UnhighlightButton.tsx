import React from 'react';
import { useChatContext } from '../../contexts/ChatContext';

interface UnhighlightButtonProps {
  className?: string;
}

export const UnhighlightButton: React.FC<UnhighlightButtonProps> = ({ 
  className = '' 
}) => {
  const { highlightedText, clearAllTextHighlights } = useChatContext();

  // Only show the button if there's highlighted text
  if (!highlightedText || !highlightedText.trim()) {
    return null;
  }

  const handleUnhighlight = () => {
    clearAllTextHighlights();
  };

  return (
    <button
      onClick={handleUnhighlight}
      className={`unhighlight-button ${className}`}
      title="Remove all text highlights"
      aria-label="Remove all text highlights"
    >
      🧹 Unhighlight
    </button>
  );
}; 