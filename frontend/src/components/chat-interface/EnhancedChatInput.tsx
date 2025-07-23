/**
 * EnhancedChatInput Component
 * 
 * Enhanced chat input with suggestions button for Co-Edit mode.
 * Provides different UI based on the selected AI mode.
 */

import React, { useState, useRef, useEffect } from 'react';
import { useChatContext } from '../../contexts/ChatContext';

interface EnhancedChatInputProps {
  onSendMessage: (message: string) => void;
  isLoading?: boolean;
  placeholder?: string;
}

export const EnhancedChatInput: React.FC<EnhancedChatInputProps> = ({
  onSendMessage,
  isLoading = false,
  placeholder = "Ask Owen anything about your writing..."
}) => {
  const { 
    handleSendMessage, 
    isThinking, 
    isStreaming, 
    highlightedText,
    aiMode,
    currentSuggestions = [],
    isGeneratingSuggestions,
    generateTextSuggestions
  } = useChatContext();
  
  const [message, setMessage] = useState('');
  const [isExpanded, setIsExpanded] = useState(false);
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  
  // Function to recalculate textarea size
  const recalculateTextareaSize = () => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      const scrollHeight = textareaRef.current.scrollHeight;
      const maxHeight = 120;
      const newHeight = Math.min(scrollHeight, maxHeight);
      textareaRef.current.style.height = `${newHeight}px`;
      textareaRef.current.style.overflowY = scrollHeight > maxHeight ? 'auto' : 'hidden';
    }
  };

  // Auto-resize textarea with improved height calculation
  useEffect(() => {
    recalculateTextareaSize();
  }, [message]);
  
  // Handle window resize for responsive behavior
  useEffect(() => {
    const handleResize = () => {
      setTimeout(recalculateTextareaSize, 100); // Small delay to ensure layout has settled
    };
    
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (message.trim() && !isLoading) {
      onSendMessage(message.trim());
      setMessage('');
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  const handleGenerateSuggestions = async () => {
    if (!highlightedText.trim()) {
      // Show a hint to select text first
      return;
    }
    
    const suggestionMessage = message.trim() || "Please improve this text";
    await generateTextSuggestions(suggestionMessage);
    setMessage(''); // Clear input after generating suggestions
  };

  const canGenerateSuggestions = aiMode === 'co-edit' && highlightedText.trim().length > 0;
  const hasSuggestions = Array.isArray(currentSuggestions) && currentSuggestions.length > 0;

  return (
    <div className="enhanced-chat-input">
      {/* Mode indicator */}
      <div className="chat-mode-indicator">
        <span className={`mode-badge ${aiMode}`}>
          {aiMode === 'co-edit' ? '✏️ Co-Edit Mode' : '💬 Talk Mode'}
        </span>
        {aiMode === 'co-edit' && (
          <span className="mode-hint">
            {highlightedText ? 'Text selected - ready for suggestions!' : 'Select text to get improvement options'}
          </span>
        )}
      </div>

      <form onSubmit={handleSubmit} className="chat-input-form">
        <div className="input-container">
          <textarea
            ref={textareaRef}
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder={
              aiMode === 'co-edit' && highlightedText 
                ? "How would you like to improve the selected text?"
                : placeholder
            }
            disabled={isLoading || isGeneratingSuggestions}
            className="chat-textarea"
            rows={1}
            maxLength={2000}
          />
          
          <div className="input-actions">
            {/* Suggestions button for Co-Edit mode */}
            {canGenerateSuggestions && (
              <button
                type="button"
                onClick={handleGenerateSuggestions}
                disabled={isLoading || isGeneratingSuggestions}
                className="suggestions-button"
                title="Generate multiple improvement options"
              >
                {isGeneratingSuggestions ? (
                  <span className="loading-spinner">⏳</span>
                ) : (
                  <span className="suggestions-icon">✨</span>
                )}
                {isGeneratingSuggestions ? 'Generating...' : 'Get Options'}
              </button>
            )}
            
            {/* Regular send button */}
            <button
              type="submit"
              disabled={!message.trim() || isLoading || isGeneratingSuggestions}
              className="send-button"
              title={aiMode === 'co-edit' ? 'Send for direct editing' : 'Send message'}
            >
              {isLoading ? (
                <span className="loading-spinner">⏳</span>
              ) : (
                <span className="send-icon">→</span>
              )}
            </button>
          </div>
        </div>
        
        {/* Character count */}
        <div className="input-footer">
          <span className="character-count">
            {message.length}/2000
          </span>
          
          {/* Suggestions status */}
          {hasSuggestions && (
            <span className="suggestions-status">
              ✨ {currentSuggestions?.length || 0} options ready
            </span>
          )}
        </div>
      </form>
    </div>
  );
};

export default EnhancedChatInput; 