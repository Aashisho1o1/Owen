import React from 'react';

interface HighlightedTextDisplayProps {
  highlightedText: string;
  contextualPrompts: string[];
  onPromptClick: (prompt: string) => void;
}

/**
 * Molecular Component: Highlighted Text Display
 * Single Responsibility: Display selected text and provide contextual prompts
 * Enhanced: Shows AI analysis status and makes highlighting context clear
 */
export const HighlightedTextDisplay: React.FC<HighlightedTextDisplayProps> = ({
  highlightedText,
  contextualPrompts,
  onPromptClick
}) => {
  if (!highlightedText) return null;

  const wordCount = highlightedText.split(/\s+/).length;
  const charCount = highlightedText.length;

  return (
    <div className="highlighted-text-box">
      <div className="highlighted-title">
        🎯 AI is analyzing this selected text
      </div>
      
      <div className="highlighted-meta">
        📊 {wordCount} words • {charCount} characters
      </div>
      
      <div className="highlighted-content">
        {highlightedText}
      </div>
      
      {contextualPrompts.length > 0 && (
        <div className="contextual-prompts">
          <div className="contextual-prompts-title">💡 Quick questions about this text:</div>
          <div className="contextual-prompts-list">
            {contextualPrompts.map((prompt, index) => (
              <button
                key={index}
                className="contextual-prompt-button"
                onClick={() => onPromptClick(prompt)}
                title={`Ask: ${prompt}`}
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
 