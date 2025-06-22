import React, { useState, useEffect, useRef, useCallback } from 'react';
import { useChatContext } from '../../contexts/ChatContext';
import '../../styles/text-selection.css';

/**
 * TextSelectionHandler - Handles text selection and AI interaction
 * 
 * SINGLE RESPONSIBILITY:
 * - Manage text selection state
 * - Show/hide floating AI button
 * - Connect text selection to chat context
 * 
 * CLEAN ARCHITECTURE:
 * - Uses context for communication (no global events)
 * - Self-contained component with clear boundaries
 * - Type-safe interactions
 */

interface TextSelection {
  top: number;
  left: number;
  text: string;
}

export const TextSelectionHandler: React.FC = () => {
  const [selection, setSelection] = useState<TextSelection | null>(null);
  const editorRef = useRef<HTMLDivElement>(null);
  
  // Connect to ChatContext - proper dependency injection
  const { 
    setHighlightedText, 
    isChatVisible, 
    openChatWithText 
  } = useChatContext();

  /**
   * Handle text selection in editor
   * CLEAN: No global events, direct DOM interaction
   */
  const handleTextSelection = useCallback(() => {
    const sel = window.getSelection();
    if (!sel || sel.rangeCount === 0) {
      setSelection(null);
      return;
    }

    const selectedText = sel.toString().trim();
    if (!selectedText || selectedText.length < 3) {
      setSelection(null);
      return;
    }

    const range = sel.getRangeAt(0);
    const rect = range.getBoundingClientRect();
    
    if (editorRef.current) {
      const editorRect = editorRef.current.getBoundingClientRect();
      
      // Calculate position relative to editor
      let top = rect.top - editorRect.top + rect.height + 8;
      let left = rect.left - editorRect.left + rect.width / 2;
      
      // Bounds checking
      const editorWidth = editorRect.width;
      const editorHeight = editorRect.height;
      
      // Adjust for chat panel if visible
      if (isChatVisible) {
        const maxLeft = editorWidth * 0.6 - 80; // Account for chat panel
        left = Math.min(left, maxLeft);
      }
      
      // Keep within bounds
      left = Math.max(80, Math.min(left, editorWidth - 80));
      top = Math.max(10, Math.min(top, editorHeight - 50));
      
      setSelection({
        top,
        left,
        text: selectedText,
      });
    }
  }, [isChatVisible]);

  /**
   * Handle AI interaction with selected text
   * CLEAN: Uses context methods, no global events
   */
  const handleAskAI = useCallback(() => {
    if (!selection) return;

    // Update highlighted text in context
    setHighlightedText(selection.text);
    
    // Open chat with the selected text
    openChatWithText(selection.text);
    
    // Clear selection
    setSelection(null);
  }, [selection, setHighlightedText, openChatWithText]);

  /**
   * Set up event listeners for text selection
   * CLEAN: Component-scoped events, not global
   */
  useEffect(() => {
    const editorElement = editorRef.current;
    if (!editorElement) return;

    // Listen for mouse up events on the editor
    const handleMouseUp = () => {
      // Small delay to ensure selection is complete
      setTimeout(handleTextSelection, 10);
    };

    const handleKeyUp = (e: KeyboardEvent) => {
      // Handle keyboard selection (Shift + Arrow keys)
      if (e.shiftKey) {
        setTimeout(handleTextSelection, 10);
      }
    };

    editorElement.addEventListener('mouseup', handleMouseUp);
    editorElement.addEventListener('keyup', handleKeyUp);

    return () => {
      editorElement.removeEventListener('mouseup', handleMouseUp);
      editorElement.removeEventListener('keyup', handleKeyUp);
    };
  }, [handleTextSelection]);

  return (
    <>
      {/* Hidden ref element for editor boundary detection */}
      <div ref={editorRef} className="text-selection-boundary" />
      
      {/* Floating AI Button */}
      {selection && (
        <button
          className="floating-ai-button"
          style={{ 
            top: selection.top, 
            left: selection.left 
          }}
          onClick={handleAskAI}
          aria-label={`Ask AI about selected text: ${selection.text.substring(0, 50)}...`}
        >
          ✨ Ask AI
        </button>
      )}
    </>
  );
};

export default TextSelectionHandler; 