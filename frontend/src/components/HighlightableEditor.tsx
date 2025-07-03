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
import { createPortal } from 'react-dom';

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

  // Handle text selection for floating AI button
  const handleTextSelection = useCallback((selectedText: string, editorView: { state: { selection: { from: number; to: number } }; coordsAtPos: (pos: number) => { top: number; bottom: number; left: number; right: number } }) => {
    console.log('🎯 handleTextSelection called with:', selectedText);
    
    if (!selectedText || selectedText.length < 3) {
      setSelection(null);
      return;
    }
    
    // Get selection coordinates from the editor view
    const { from, to } = editorView.state.selection;
    const startCoords = editorView.coordsAtPos(from);
    const endCoords = editorView.coordsAtPos(to);
    
    console.log('📐 Selection coordinates:', { startCoords, endCoords });
    
    // Since we're using position: fixed, we need viewport coordinates
    // The coordsAtPos already returns viewport coordinates
    const viewportTop = endCoords.bottom + 10; // Position below selection
    const viewportLeft = (startCoords.left + endCoords.right) / 2; // Center horizontally
    
    // Get viewport dimensions
    const viewportHeight = window.innerHeight;
    const viewportWidth = window.innerWidth;
    
    // Ensure button stays within viewport bounds
    const buttonWidth = 100; // Approximate button width
    const buttonHeight = 40; // Approximate button height
    
    let finalTop = viewportTop;
    let finalLeft = viewportLeft;
    
    // Vertical bounds check
    if (finalTop + buttonHeight > viewportHeight) {
      // Position above selection if too close to bottom
      finalTop = startCoords.top - buttonHeight - 10;
    }
    
    // Horizontal bounds check
    if (finalLeft - buttonWidth/2 < 0) {
      finalLeft = buttonWidth/2 + 10;
    } else if (finalLeft + buttonWidth/2 > viewportWidth) {
      finalLeft = viewportWidth - buttonWidth/2 - 10;
    }
    
    console.log('🎯 Final button position:', { 
      finalTop, 
      finalLeft,
      viewportHeight,
      viewportWidth
    });
    
    setSelection({
      text: selectedText,
      top: finalTop,
      left: finalLeft
    });
  }, []);

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
    // ADDED: Handle text selection updates for floating AI button with debouncing
    onSelectionUpdate: (() => {
      let debounceTimeout: NodeJS.Timeout;
      let lastSelection = { from: -1, to: -1 };
      
      return ({ editor }) => {
        if (debounceTimeout) {
          clearTimeout(debounceTimeout);
        }
        
        debounceTimeout = setTimeout(() => {
          console.log('🎯 onSelectionUpdate triggered');
          const { from, to } = editor.state.selection;
          
          // Skip if same selection as before
          if (from === lastSelection.from && to === lastSelection.to) return;
          lastSelection = { from, to };
          
          const selectedText = editor.state.doc.textBetween(from, to, ' ').trim();
          
          console.log('📝 Selection details:', { from, to, selectedText, length: selectedText.length });
          
          if (selectedText && selectedText.length >= 3) {
            // Call our text selection handler with the selected text and editor view
            handleTextSelection(selectedText, editor.view);
          } else {
            // Clear selection if no meaningful text is selected
            setSelection(null);
          }
        }, 100); // 100ms debounce
      };
    })(),
    // ALTERNATIVE: Use transaction event as more reliable selection detection with debouncing
    onTransaction: (() => {
      let debounceTimeout: NodeJS.Timeout;
      let lastSelection = { from: -1, to: -1 };
      
      return ({ editor, transaction }) => {
        // Only process if selection actually changed
        if (transaction.selectionSet) {
          if (debounceTimeout) {
            clearTimeout(debounceTimeout);
          }
          
          debounceTimeout = setTimeout(() => {
            console.log('🔄 Transaction with selection change detected');
            const { from, to } = editor.state.selection;
            
            // Skip if same selection as before
            if (from === lastSelection.from && to === lastSelection.to) return;
            lastSelection = { from, to };
            
            const selectedText = editor.state.doc.textBetween(from, to, ' ').trim();
            
            console.log('📝 Transaction selection details:', { from, to, selectedText, length: selectedText.length });
            
            if (selectedText && selectedText.length >= 3) {
              // Call our text selection handler with the selected text and editor view
              handleTextSelection(selectedText, editor.view);
            } else {
              // Clear selection if no meaningful text is selected
              setSelection(null);
            }
          }, 100); // 100ms debounce
        }
      };
    })(),
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

  // BACKUP: Add DOM-based text selection detection as fallback
  useEffect(() => {
    let debounceTimeout: NodeJS.Timeout;
    let lastSelectedText = '';
    
    const handleDocumentSelectionChange = () => {
      // Clear previous timeout
      if (debounceTimeout) {
        clearTimeout(debounceTimeout);
      }
      
      // Debounce the selection handling to prevent excessive firing
      debounceTimeout = setTimeout(() => {
        const selection = window.getSelection();
        if (!selection || !editorRef.current) return;
        
        const selectedText = selection.toString().trim();
        
        // Skip if same text as before to prevent duplicate processing
        if (selectedText === lastSelectedText) return;
        lastSelectedText = selectedText;
        
        console.log('🔄 DOM selection change detected:', { selectedText, length: selectedText.length });
        
        // Check if selection is within our editor
        if (selection.rangeCount > 0) {
          const range = selection.getRangeAt(0);
          const isWithinEditor = editorRef.current.contains(range.commonAncestorContainer);
          
          console.log('📍 Selection location check:', { isWithinEditor, selectedText });
          
          if (isWithinEditor && selectedText && selectedText.length >= 3) {
            console.log('✅ Valid selection within editor, calling fallback handler');
            fallbackTextSelection(selectedText);
          } else if (!selectedText || selectedText.length < 3) {
            setSelection(null);
          }
        }
      }, 150); // 150ms debounce delay
    };

    // ENHANCED: Multiple event listeners for maximum compatibility
    const events = ['selectionchange', 'mouseup', 'keyup', 'touchend'];
    
    // Add global document listener
    document.addEventListener('selectionchange', handleDocumentSelectionChange);
    
    // Add editor-specific listeners with throttling
    const editorElement = editorRef.current;
    if (editorElement) {
      let throttleTimeout: NodeJS.Timeout | null = null;
      
      const throttledHandler = () => {
        if (throttleTimeout) return; // Skip if already throttled
        
        throttleTimeout = setTimeout(() => {
          handleDocumentSelectionChange();
          throttleTimeout = null;
        }, 100); // 100ms throttle
      };
      
      events.forEach(event => {
        editorElement.addEventListener(event, throttledHandler);
      });
    }
    
    return () => {
      if (debounceTimeout) {
        clearTimeout(debounceTimeout);
      }
      document.removeEventListener('selectionchange', handleDocumentSelectionChange);
      if (editorElement) {
        events.forEach(event => {
          editorElement.removeEventListener(event, handleDocumentSelectionChange);
        });
      }
    };
  }, [fallbackTextSelection]);
  
  // Auto-focus editor when component mounts or when user clicks
  useEffect(() => {
    if (editor && editorRef.current) {
      // Set up click handler to focus editor
      const handleContainerClick = (e: MouseEvent) => {
        if (e.target === editorRef.current || editorRef.current?.contains(e.target as Node)) {
          editor.commands.focus();
        }
      };
      
      editorRef.current.addEventListener('click', handleContainerClick);
      
      // Auto-focus on mount to show cursor immediately
      setTimeout(() => {
        editor.commands.focus();
      }, 200);
      
      return () => {
        editorRef.current?.removeEventListener('click', handleContainerClick);
      };
    }
  }, [editor]);

          return (
    <div className="highlightable-editor-container">
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
        
        {/* DEBUG: Visual indicator for selection state */}
        {process.env.NODE_ENV === 'development' && (
          <div style={{
            position: 'absolute',
            top: '5px',
            right: '5px',
            background: 'rgba(0,0,0,0.8)',
            color: 'white',
            padding: '4px 8px',
            borderRadius: '4px',
            fontSize: '10px',
            zIndex: 2000,
            pointerEvents: 'none'
          }}>
            Selection: {selection ? `"${selection.text.substring(0, 20)}..." (${selection.top}, ${selection.left})` : 'None'}
          </div>
        )}
      </div>
      
      {/* Floating AI Button for text selection - rendered outside editor wrapper using portal */}
      {selection && createPortal(
        <button
          className="floating-ai-button"
          style={{ 
            position: 'fixed',
            top: selection.top, 
            left: selection.left,
            zIndex: 10000
          }}
          onClick={handleAskAI}
          aria-label={`Ask AI about selected text: ${selection.text.substring(0, 50)}...`}
        >
          ✨ Ask AI
        </button>,
        document.body
      )}
    </div>
  );
};

export default HighlightableEditor; 