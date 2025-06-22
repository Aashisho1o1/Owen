/**
 * HighlightableEditor Component - Clean Architecture Implementation
 * 
 * REFACTORED using Atomic Design principles:
 * - Single Responsibility: Coordinate highlighting workflow
 * - Delegates specific responsibilities to focused sub-components
 * - Uses composition over complex state management
 * - Follows React best practices for maintainability
 */

import React, { useEffect, useRef, useCallback, useState } from 'react';
import { useEditor, EditorContent } from '@tiptap/react';
import StarterKit from '@tiptap/starter-kit';
import { useEditorContext } from '../contexts/EditorContext';
import { useChatContext } from '../contexts/ChatContext';
import '../styles/highlightable-editor.css';

interface HighlightableEditorProps {
  content?: string;
  onChange?: (content: string) => void;
}

/**
 * Simple HighlightableEditor that works with CSS-based highlighting
 * Uses DOM manipulation for highlighting which is simpler and more reliable
 */
const HighlightableEditor: React.FC<HighlightableEditorProps> = ({
  content,
  onChange
}) => {
  const { 
    editorContent: contextContent, 
    setEditorContent: contextOnChange
  } = useEditorContext();

  // Use props if provided, otherwise use context
  const contentProp = content !== undefined ? content : contextContent;
  const onChangeProp = onChange || contextOnChange;

  const editor = useEditor({
    extensions: [
      StarterKit,
    ],
    content: contentProp || '',
    onUpdate: ({ editor }) => {
      const newContent = editor.getHTML();
      onChangeProp(newContent);
    },
  });

  // Handle active discussion highlighting from ChatContext using DOM manipulation
  useEffect(() => {
    const handleActiveDiscussionHighlight = (event: CustomEvent) => {
      if (!editor) return;

      const { text, action } = event.detail;
      const editorElement = editor.view.dom;
      
      console.log('🎯 HIGHLIGHT EVENT:', { text, action, hasEditor: !!editor });
      
      if (action === 'add' && text) {
        // Remove existing highlights first
        const existingHighlights = editorElement.querySelectorAll('.active-discussion-highlight');
        console.log('🧹 Removing', existingHighlights.length, 'existing highlights');
        existingHighlights.forEach(el => {
          const parent = el.parentNode;
          if (parent) {
            parent.replaceChild(document.createTextNode(el.textContent || ''), el);
            parent.normalize();
          }
        });
        
        // Get all text content and find the text to highlight
        const allText = editorElement.textContent || '';
        const textIndex = allText.indexOf(text);
        console.log('🔍 Looking for text:', text, 'in editor content, found at index:', textIndex);
        
        if (textIndex >= 0) {
          // Use a more robust text search and highlight approach
          const walker = document.createTreeWalker(
            editorElement,
            NodeFilter.SHOW_TEXT,
            null
          );
          
                     let currentOffset = 0;
           const targetStartOffset = textIndex;
           const targetEndOffset = textIndex + text.length;
          let textNode;
          
          while ((textNode = walker.nextNode())) {
            const nodeValue = textNode.nodeValue || '';
            const nodeLength = nodeValue.length;
            
            // Check if our target text spans this node
            if (currentOffset <= targetStartOffset && (currentOffset + nodeLength) >= targetStartOffset) {
              const startInNode = targetStartOffset - currentOffset;
              const endInNode = Math.min(targetEndOffset - currentOffset, nodeLength);
              
              console.log('🎯 Found text node to highlight:', {
                nodeValue: nodeValue.substring(0, 50),
                startInNode,
                endInNode,
                textToHighlight: nodeValue.substring(startInNode, endInNode)
              });
              
              // Split the text node if necessary and wrap the target text
              const beforeText = nodeValue.substring(0, startInNode);
              const highlightText = nodeValue.substring(startInNode, endInNode);
              const afterText = nodeValue.substring(endInNode);
              
              // Create the highlight span
              const highlightSpan = document.createElement('span');
              highlightSpan.className = 'active-discussion-highlight';
              highlightSpan.textContent = highlightText;
              highlightSpan.style.cssText = `
                background: #ffeb3b !important;
                color: #d84315 !important;
                border: 2px solid #ff9800 !important;
                border-radius: 4px !important;
                padding: 2px 4px !important;
                font-weight: bold !important;
                text-decoration: underline !important;
                text-decoration-color: #ff9800 !important;
                box-shadow: 0 0 8px rgba(255, 152, 0, 0.5) !important;
                display: inline !important;
              `;
              
              // Replace the text node with our highlighted version
              const parent = textNode.parentNode;
              if (parent) {
                if (beforeText) {
                  parent.insertBefore(document.createTextNode(beforeText), textNode);
                }
                parent.insertBefore(highlightSpan, textNode);
                if (afterText) {
                  parent.insertBefore(document.createTextNode(afterText), textNode);
                }
                parent.removeChild(textNode);
                
                console.log('✅ Successfully applied highlight to text:', highlightText);
              }
              break;
            }
            
            currentOffset += nodeLength;
          }
        } else {
          console.warn('❌ Text not found in editor content');
        }
      } else if (action === 'remove') {
        // Remove all highlights
        const highlights = editorElement.querySelectorAll('.active-discussion-highlight');
        console.log('🧹 Removing all highlights:', highlights.length);
        highlights.forEach(el => {
          const parent = el.parentNode;
          if (parent) {
            parent.replaceChild(document.createTextNode(el.textContent || ''), el);
            parent.normalize();
          }
        });
      }
    };

    window.addEventListener('applyActiveDiscussionHighlight', handleActiveDiscussionHighlight as EventListener);
    
    return () => {
      window.removeEventListener('applyActiveDiscussionHighlight', handleActiveDiscussionHighlight as EventListener);
    };
  }, [editor]);

  // Update editor content when the content prop changes
  useEffect(() => {
    if (editor && contentProp && editor.getHTML() !== contentProp) {
      editor.commands.setContent(contentProp);
    }
  }, [contentProp, editor]);

  // Text selection state
  const [selection, setSelection] = useState<{top: number; left: number; text: string} | null>(null);
  const editorRef = useRef<HTMLDivElement>(null);
  
  // Chat context for highlighting
  const { 
    setHighlightedText, 
    handleTextHighlighted,
    isChatVisible, 
    openChatWithText 
  } = useChatContext();

  // Handle text selection in editor
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

  // Handle AI interaction with selected text
  const handleAskAI = useCallback(() => {
    if (!selection) return;

    console.log('🤖 Asking AI about selected text:', selection.text);

    // Apply visual highlighting through ChatContext
    handleTextHighlighted(selection.text);
    
    // Update highlighted text in context (for chat display)
    setHighlightedText(selection.text);
    
    // Open chat with the selected text
    openChatWithText(selection.text);
    
    // Clear selection
    setSelection(null);
  }, [selection, handleTextHighlighted, setHighlightedText, openChatWithText]);

  // Set up event listeners for text selection
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
    <div className="highlightable-editor-container">
      <div ref={editorRef} className="editor-wrapper">
        <EditorContent 
          editor={editor} 
          className="highlightable-editor"
        />
        
        {/* Floating AI Button for text selection */}
        {selection && (
          <button
            className="floating-ai-button"
            style={{ 
              position: 'absolute',
              top: selection.top, 
              left: selection.left,
              zIndex: 1000,
              background: '#3b82f6',
              color: 'white',
              border: 'none',
              borderRadius: '8px',
              padding: '8px 12px',
              fontSize: '14px',
              fontWeight: '600',
              cursor: 'pointer',
              boxShadow: '0 4px 12px rgba(59, 130, 246, 0.3)',
              animation: 'fadeIn 0.2s ease-out'
            }}
            onClick={handleAskAI}
            aria-label={`Ask AI about selected text: ${selection.text.substring(0, 50)}...`}
          >
            ✨ Ask AI
          </button>
        )}
      </div>
    </div>
  );
};

export default HighlightableEditor; 