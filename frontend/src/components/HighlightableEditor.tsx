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
        // Remove existing highlights first - IMPROVED cleanup
        const existingHighlights = editorElement.querySelectorAll('.active-discussion-highlight');
        console.log('🧹 Removing', existingHighlights.length, 'existing highlights');
        existingHighlights.forEach(el => {
          const parent = el.parentNode;
          if (parent) {
            // Create a text node with the original content
            const textNode = document.createTextNode(el.textContent || '');
            parent.replaceChild(textNode, el);
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
              
              // Create the highlight span with MINIMAL inline styles (let CSS handle it)
              const highlightSpan = document.createElement('span');
              highlightSpan.className = 'active-discussion-highlight';
              highlightSpan.textContent = highlightText;
              // REMOVED inline styles - let CSS handle all styling to avoid conflicts
              
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
        // IMPROVED: Remove all highlights with better cleanup
        const highlights = editorElement.querySelectorAll('.active-discussion-highlight');
        console.log('🧹 Removing all highlights:', highlights.length);
        
        highlights.forEach(el => {
          const parent = el.parentNode;
          if (parent) {
            // Create a clean text node without any styling
            const textNode = document.createTextNode(el.textContent || '');
            parent.replaceChild(textNode, el);
          }
        });
        
        // Normalize all text nodes to merge adjacent ones
        const walker = document.createTreeWalker(
          editorElement,
          NodeFilter.SHOW_ELEMENT,
          null
        );
        
        let element;
        const elementsToNormalize = [editorElement];
        while ((element = walker.nextNode())) {
          if (element instanceof HTMLElement) {
            elementsToNormalize.push(element);
          }
        }
        
        // Normalize in reverse order to avoid DOM structure changes affecting traversal
        elementsToNormalize.reverse().forEach(el => {
          if (el && typeof el.normalize === 'function') {
            el.normalize();
          }
        });
        
        console.log('🧹 Completed highlight removal and text normalization');
      } else if (action === 'clear-all') {
        // ENHANCED: Clear all highlights with comprehensive cleanup
        const highlights = editorElement.querySelectorAll('.active-discussion-highlight');
        console.log('🧹 CLEAR-ALL: Removing all highlights:', highlights.length);
        
        // Store parent elements that need normalization
        const parentsToNormalize = new Set();
        
        highlights.forEach(el => {
          const parent = el.parentNode;
          if (parent) {
            parentsToNormalize.add(parent);
            // Create a completely clean text node
            const textNode = document.createTextNode(el.textContent || '');
            parent.replaceChild(textNode, el);
          }
        });
        
        // Normalize all affected parent elements to merge text nodes
        parentsToNormalize.forEach(parent => {
          if (parent && typeof (parent as any).normalize === 'function') {
            (parent as HTMLElement).normalize();
          }
        });
        
        // Also normalize the entire editor to ensure clean state
        if (editorElement.normalize) {
          editorElement.normalize();
        }
        
        console.log('🧹 CLEAR-ALL: Completed comprehensive cleanup and normalization');
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
              top: selection.top, 
              left: selection.left
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