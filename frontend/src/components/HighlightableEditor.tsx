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
 * Custom Blinking Cursor Component
 * Provides a visual cursor when the native cursor might not be visible
 */
const BlinkingCursor: React.FC<{ show: boolean }> = ({ show }) => {
  const [isVisible, setIsVisible] = useState(true);

  useEffect(() => {
    if (!show) return;

    const interval = setInterval(() => {
      setIsVisible(prev => !prev);
    }, 500); // Blink every 500ms

    return () => clearInterval(interval);
  }, [show]);

  if (!show) return null;

  return (
    <span 
      className="custom-blinking-cursor"
      style={{
        display: 'inline-block',
        width: '2px',
        height: '1.2em',
        backgroundColor: '#2563eb',
        marginLeft: '1px',
        opacity: isVisible ? 1 : 0,
        transition: 'opacity 0.1s ease',
        position: 'relative',
        top: '0.1em'
      }}
    >
      |
    </span>
  );
};

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
      console.log('🔧 HighlightableEditor onUpdate:', {
        newContentLength: newContent.length,
        newContentPreview: newContent.substring(0, 100) + '...',
        onChangePropType: typeof onChangeProp,
        hasOnChangeProp: !!onChangeProp
      });
      onChangeProp(newContent);
    },
    // ADDED: Handle text selection updates for floating AI button
    onSelectionUpdate: ({ editor }) => {
      const { from, to } = editor.state.selection;
      const selectedText = editor.state.doc.textBetween(from, to, ' ').trim();
      
      if (selectedText && selectedText.length >= 3) {
        // Call our text selection handler with the selected text and editor view
        handleTextSelection(selectedText, editor.view);
      } else {
        // Clear selection if no meaningful text is selected
        setSelection(null);
      }
    },
    // Add editor event handlers for better cursor management
    onCreate: ({ editor }) => {
      // Auto-focus the editor when it's created to show cursor
      setTimeout(() => {
        editor.commands.focus();
      }, 100);
    },
    onFocus: () => {
      // Ensure cursor is visible when editor gains focus
      console.log('🎯 Editor focused - cursor should be visible');
      setEditorHasFocus(true);
      setShowCustomCursor(false); // Hide custom cursor when native focus is available
    },
    onBlur: () => {
      // Log when editor loses focus for debugging
      console.log('🎯 Editor blurred');
      setEditorHasFocus(false);
      // Show custom cursor if editor is empty and loses focus
      setTimeout(() => {
        if (editor && editor.getHTML().replace(/<[^>]*>/g, '').trim().length === 0) {
          setShowCustomCursor(true);
        }
      }, 100);
    },
  });

  // Handle active discussion highlighting from ChatContext using DOM manipulation
  useEffect(() => {
    let isMounted = true; // MEMORY LEAK FIX: Track component mount state
    
    const handleActiveDiscussionHighlight = (event: CustomEvent) => {
      if (!editor || !isMounted) return; // MEMORY LEAK FIX: Check if component is still mounted

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
            // SECURITY: Safely create text node with sanitized content
            const textContent = el.textContent || '';
            // Sanitize the text content to prevent any potential XSS
            const sanitizedText = textContent.replace(/[<>&"']/g, '');
            const textNode = document.createTextNode(sanitizedText);
            parent.replaceChild(textNode, el);
          }
        });
        
        // Normalize all affected parent elements to merge text nodes
        parentsToNormalize.forEach(parent => {
          if (parent && parent instanceof HTMLElement && typeof parent.normalize === 'function') {
            parent.normalize();
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
      isMounted = false; // MEMORY LEAK FIX: Mark component as unmounted
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
  
  // Custom cursor state for enhanced visibility
  const [showCustomCursor, setShowCustomCursor] = useState(false);
  const [editorHasFocus, setEditorHasFocus] = useState(false);
  
  // Chat context for highlighting
  const { 
    setHighlightedText, 
    handleTextHighlighted,
    isChatVisible, 
    openChatWithText 
  } = useChatContext();

  // Fallback text selection detection using DOM selection
  const fallbackTextSelection = useCallback((selectedText: string) => {
    const sel = window.getSelection();
    if (!sel || sel.rangeCount === 0) return;

    const range = sel.getRangeAt(0);
    const rect = range.getBoundingClientRect();
    
    if (editorRef.current) {
      const editorRect = editorRef.current.getBoundingClientRect();
      
      let top = rect.bottom - editorRect.top + 8;
      let left = rect.left + rect.width / 2 - editorRect.left;
      
      const editorWidth = editorRect.width;
      const editorHeight = editorRect.height;
      
      if (isChatVisible) {
        const maxLeft = editorWidth * 0.6 - 80;
        left = Math.min(left, maxLeft);
      }
      
      left = Math.max(80, Math.min(left, editorWidth - 80));
      top = Math.max(10, Math.min(top, editorHeight - 50));
      
      setSelection({
        top,
        left,
        text: selectedText,
      });
      
      console.log('✅ Text selection detected via fallback DOM method:', {
        text: selectedText.substring(0, 50) + '...',
        position: { top, left }
      });
    }
  }, [isChatVisible]);

  // Handle text selection in editor - FIXED: Now uses TipTap's selection system
  const handleTextSelection = useCallback((selectedText: string, editorView?: { state: { selection: { from: number; to: number } }; coordsAtPos: (pos: number) => { top: number; left: number } }) => {
    if (!selectedText || selectedText.length < 3) {
      setSelection(null);
      return;
    }

    // Use TipTap's editor view to get selection coordinates if available
    if (editorView && editorRef.current) {
      try {
        const { from, to } = editorView.state.selection;
        const start = editorView.coordsAtPos(from);
        const end = editorView.coordsAtPos(to);
        
        const editorRect = editorRef.current.getBoundingClientRect();
        
        // Calculate position relative to editor wrapper
        let top = Math.max(start.top, end.top) - editorRect.top + 8;
        let left = (start.left + end.left) / 2 - editorRect.left;
        
        // Bounds checking
        const editorWidth = editorRect.width;
        const editorHeight = editorRect.height;
        
        // Adjust for chat panel if visible
        if (isChatVisible) {
          const maxLeft = editorWidth * 0.6 - 80;
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
        
        console.log('✅ Text selection detected via TipTap:', {
          text: selectedText.substring(0, 50) + '...',
          position: { top, left }
        });
        
      } catch {
        console.warn('⚠️ Failed to get TipTap selection coordinates, falling back to manual detection');
        // Fallback to manual detection
        fallbackTextSelection(selectedText);
      }
    } else {
      // Fallback to manual detection
      fallbackTextSelection(selectedText);
    }
  }, [isChatVisible, fallbackTextSelection]);

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

  // Enhanced focus management for cursor visibility
  const editorContainerRef = useRef<HTMLDivElement>(null);
  
  // Auto-focus editor when component mounts or when user clicks
  useEffect(() => {
    if (editor && editorContainerRef.current) {
      // Set up click handler to focus editor
      const handleContainerClick = (e: MouseEvent) => {
        if (e.target === editorContainerRef.current || editorContainerRef.current?.contains(e.target as Node)) {
          editor.commands.focus();
        }
      };
      
      editorContainerRef.current.addEventListener('click', handleContainerClick);
      
      // Auto-focus on mount to show cursor immediately
      setTimeout(() => {
        editor.commands.focus();
      }, 200);
      
      return () => {
        editorContainerRef.current?.removeEventListener('click', handleContainerClick);
      };
    }
  }, [editor]);

          return (
    <div className="highlightable-editor-container" ref={editorContainerRef}>
      <div ref={editorRef} className="editor-wrapper">
        <EditorContent 
          editor={editor} 
          className="highlightable-editor"
        />
        
        {/* Custom blinking cursor for enhanced visibility */}
        {showCustomCursor && !editorHasFocus && (
          <div 
            style={{
              position: 'absolute',
              top: '24px',
              left: '28px',
              pointerEvents: 'none',
              zIndex: 1000
            }}
          >
            <BlinkingCursor show={true} />
          </div>
        )}
        
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