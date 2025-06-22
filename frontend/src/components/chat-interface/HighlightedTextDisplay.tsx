import React from 'react';

interface HighlightedTextDisplayProps {
  highlightedText: string;
  contextualPrompts: string[];
  onPromptClick: (prompt: string) => void;
}

/**
 * Molecular Component: Highlighted Text Display
 * Single Responsibility: Display selected text and provide contextual prompts
 */
export const HighlightedTextDisplay: React.FC<HighlightedTextDisplayProps> = ({
  highlightedText,
  contextualPrompts,
  onPromptClick
}) => {
  if (!highlightedText) return null;

  return (
    <div className="highlighted-text-box">
      <div className="highlighted-title">📝 Selected Text for Analysis:</div>
      <div className="highlighted-content">"{highlightedText}"</div>
      
      {contextualPrompts.length > 0 && (
        <div className="contextual-prompts">
          <div className="contextual-prompts-title">💡 Ask me about this text:</div>
          <div className="contextual-prompts-list">
            {contextualPrompts.map((prompt, index) => (
              <button
                key={index}
                className="contextual-prompt-button"
                onClick={() => onPromptClick(prompt)}
              >
                {prompt}
              </button>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}; 
 