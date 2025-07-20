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
import { EditorView } from '@tiptap/pm/view';
import StarterKit from '@tiptap/starter-kit';
import { useEditorContext } from '../contexts/EditorContext';
import { useChatContext } from '../contexts/ChatContext';
import '../styles/highlightable-editor.css';
import '../styles/voice-consistency-underlines.css';
import { createPortal } from 'react-dom';
import { useAuth } from '../contexts/AuthContext';
import { 
  analyzeVoiceConsistency, 
  VoiceConsistencyResult 
} from '../services/api/character-voice';

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
  const { isAuthenticated } = useAuth();

  // Use props if provided, otherwise use context
  const contentProp = content !== undefined ? content : contextContent;
  const onChangeProp = onChange || contextOnChange;

  // DEBUG: Log content changes
  useEffect(() => {
    console.log('📝 Content tracking:', {
      contentProp: contentProp?.length || 0,
      contentPreview: contentProp?.substring(0, 100) || 'No content',
      contentSource: content !== undefined ? 'props' : 'context',
      contextContent: contextContent?.length || 0,
      propsContent: content?.length || 0
    });
  }, [contentProp, contextContent, content]);

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
  
  // Voice consistency analysis
  const [voiceConsistencyResults, setVoiceConsistencyResults] = useState<VoiceConsistencyResult[]>([]);
  
  // Fallback text selection handler for DOM-based selection detection
  const fallbackTextSelection = useCallback((selectedText: string) => {
    console.log('📍 Fallback text selection handler called:', { selectedText });
    
    if (!selectedText || selectedText.length < 3) {
      setSelection(null);
      return;
    }
    
    // Get the current selection position for floating button placement
    const domSelection = window.getSelection();
    if (domSelection && domSelection.rangeCount > 0) {
      const range = domSelection.getRangeAt(0);
      const rect = range.getBoundingClientRect();
      
      setSelection({
        top: rect.bottom + window.scrollY + 5,
        left: rect.left + window.scrollX,
        text: selectedText
      });
      
      console.log('✅ Fallback selection set:', { 
        text: selectedText.substring(0, 50), 
        position: { top: rect.bottom + window.scrollY + 5, left: rect.left + window.scrollX }
      });
    }
  }, []);
  
  // Main text selection handler (used by TipTap events)
  const handleTextSelection = useCallback((selectedText: string, editorView?: EditorView) => {
    console.log('🎯 Main text selection handler called:', { selectedText });
    
    if (!selectedText || selectedText.length < 3) {
      setSelection(null);
      return;
    }
    
    // Try to get position from editor view first, then fall back to DOM selection
    let position = { top: 0, left: 0 };
    
    if (editorView) {
      try {
        const { from, to } = editorView.state.selection;
        const start = editorView.coordsAtPos(from);
        const end = editorView.coordsAtPos(to);
        
        position = {
          top: end.bottom + 5,
          left: start.left
        };
      } catch (error) {
        console.warn('Could not get position from editor view:', error);
        // Fall back to DOM selection
        const domSelection = window.getSelection();
        if (domSelection && domSelection.rangeCount > 0) {
          const range = domSelection.getRangeAt(0);
          const rect = range.getBoundingClientRect();
          position = {
            top: rect.bottom + window.scrollY + 5,
            left: rect.left + window.scrollX
          };
        }
      }
    } else {
      // Use DOM selection as fallback
      const domSelection = window.getSelection();
      if (domSelection && domSelection.rangeCount > 0) {
        const range = domSelection.getRangeAt(0);
        const rect = range.getBoundingClientRect();
        position = {
          top: rect.bottom + window.scrollY + 5,
          left: rect.left + window.scrollX
        };
      }
    }
    
    setSelection({
      top: position.top,
      left: position.left,
      text: selectedText
    });
    
    console.log('✅ Main selection set:', { 
      text: selectedText.substring(0, 50), 
      position 
    });
  }, []);
  
  // Handle Ask AI button click
  const handleAskAI = useCallback(() => {
    if (!selection) return;
    
    console.log('🤖 Ask AI clicked with selection:', selection.text.substring(0, 50));
    
    // Set highlighted text in chat context
    setHighlightedText(selection.text);
    handleTextHighlighted(selection.text);
    
    // Open chat if not visible
    if (!isChatVisible) {
      openChatWithText(selection.text);
    }
    
    // Clear the selection after handling
    setSelection(null);
  }, [selection, setHighlightedText, handleTextHighlighted, isChatVisible, openChatWithText]);
  
  const editor = useEditor({
    extensions: [
      StarterKit,
    ],
    content: contentProp || '',
    onUpdate: async ({ editor }) => {
      const newContent = editor.getHTML();
      onChangeProp(newContent);
      
      // Only run voice analysis for authenticated users with sufficient content
      if (isAuthenticated && newContent && newContent.trim().length > 50) {
        try {
          const response = await analyzeVoiceConsistency(newContent);
          setVoiceConsistencyResults(response.results);
          applyVoiceInconsistencyUnderlines(response.results);
        } catch (error) {
          console.error("Error during voice consistency analysis:", error);
          setVoiceConsistencyResults([]);
        }
      } else {
        setVoiceConsistencyResults([]);
      }
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

  // Apply voice inconsistency underlines to the editor
  const applyVoiceInconsistencyUnderlines = useCallback((results: VoiceConsistencyResult[]) => {
    if (!editor) return;
    
    const editorElement = editor.view.dom;
    
    // Remove existing voice inconsistency highlights
    const existingHighlights = editorElement.querySelectorAll('.voice-inconsistent');
    existingHighlights.forEach(el => {
      const parent = el.parentNode;
      if (parent) {
        const textNode = document.createTextNode(el.textContent || '');
        parent.replaceChild(textNode, el);
        parent.normalize();
      }
    });
    
    // Apply new underlines for inconsistent dialogue
    const inconsistentResults = results.filter(result => !result.is_consistent);
    
    console.log('🎯 Applying voice inconsistency underlines:', {
      totalResults: results.length,
      inconsistentCount: inconsistentResults.length,
      inconsistentTexts: inconsistentResults.map(r => r.flagged_text.substring(0, 50))
    });
    
    // DEBUG: Test if CSS is loaded by creating a test element
    const testElement = document.createElement('span');
    testElement.className = 'voice-inconsistent';
    testElement.textContent = 'TEST';
    testElement.style.position = 'fixed';
    testElement.style.top = '10px';
    testElement.style.left = '10px';
    testElement.style.zIndex = '9999';
    testElement.style.background = 'yellow';
    document.body.appendChild(testElement);
    
    setTimeout(() => {
      const computedStyle = window.getComputedStyle(testElement);
      console.log('🧪 CSS Test Element Computed Styles:', {
        animation: computedStyle.animation,
        backgroundImage: computedStyle.backgroundImage,
        backgroundPosition: computedStyle.backgroundPosition,
        backgroundSize: computedStyle.backgroundSize
      });
      document.body.removeChild(testElement);
    }, 100);
    
    inconsistentResults.forEach(result => {
      const textToHighlight = result.flagged_text.trim();
      if (!textToHighlight) return;
      
      // Get all text content and find the text to highlight
      const allText = editorElement.textContent || '';
      const textIndex = allText.indexOf(textToHighlight);
      
      if (textIndex >= 0) {
        // Use tree walker to find and highlight the text
        const walker = document.createTreeWalker(
          editorElement,
          NodeFilter.SHOW_TEXT,
          null
        );
        
        let currentOffset = 0;
        const targetStartOffset = textIndex;
        const targetEndOffset = textIndex + textToHighlight.length;
        let textNode;
        
        while ((textNode = walker.nextNode())) {
          const nodeValue = textNode.nodeValue || '';
          const nodeLength = nodeValue.length;
          
          // Check if our target text spans this node
          if (currentOffset <= targetStartOffset && (currentOffset + nodeLength) >= targetStartOffset) {
            const startInNode = targetStartOffset - currentOffset;
            const endInNode = Math.min(targetEndOffset - currentOffset, nodeLength);
            
            // Split the text node and wrap the target text
            const beforeText = nodeValue.substring(0, startInNode);
            const highlightText = nodeValue.substring(startInNode, endInNode);
            const afterText = nodeValue.substring(endInNode);
            
            // Create the voice inconsistency span with INLINE STYLES for maximum specificity
            const inconsistencySpan = document.createElement('span');
            inconsistencySpan.className = 'voice-inconsistent';
            
            // CRITICAL FIX: Apply inline styles directly to ensure visibility in TipTap
            const confidence = result.confidence_score;
            let underlineColor = '#f59e0b'; // Default orange
            
            if (confidence <= 0.4) {
              underlineColor = '#dc2626'; // Red for high confidence issues
            } else if (confidence <= 0.7) {
              underlineColor = '#f59e0b'; // Orange for medium confidence
            } else {
              underlineColor = '#fbbf24'; // Yellow for low confidence
            }
            
            // CRITICAL FIX: Use CSS classes for animations and inline styles only for colors
            // Add confidence-based class for proper CSS cascade
            if (confidence <= 0.4) {
              inconsistencySpan.classList.add('high-confidence');
            } else if (confidence <= 0.7) {
              inconsistencySpan.classList.add('medium-confidence');
            } else {
              inconsistencySpan.classList.add('low-confidence');
            }
            
            // Apply minimal inline styles - let CSS handle animations
            inconsistencySpan.style.cssText = `
              background-image: repeating-linear-gradient(45deg, ${underlineColor} 0px, ${underlineColor} 2px, transparent 2px, transparent 4px) !important;
              cursor: pointer !important;
              display: inline !important;
              position: relative !important;
            `;
            
            // Force CSS class application by setting important properties via style
            // This ensures TipTap doesn't override our styles
            inconsistencySpan.style.setProperty('background-position', '0 100%', 'important');
            inconsistencySpan.style.setProperty('background-size', '4px 2px', 'important');
            inconsistencySpan.style.setProperty('background-repeat', 'repeat-x', 'important');
            
            // CRITICAL FIX: Force the animation to apply by setting it directly
            inconsistencySpan.style.animation = 'voice-inconsistency-wiggle 2s ease-in-out infinite !important';
            
            // Add tooltip data
            inconsistencySpan.setAttribute('data-voice-explanation', 
              `${result.explanation} (Confidence: ${Math.round(confidence * 100)}%)`);
            
            // Add accessibility attributes
            inconsistencySpan.setAttribute('role', 'button');
            inconsistencySpan.setAttribute('tabindex', '0');
            inconsistencySpan.setAttribute('aria-label', 
              `Voice inconsistency: ${result.explanation}`);
            
            // Add hover effect with inline styles for guaranteed visibility
            inconsistencySpan.addEventListener('mouseenter', () => {
              inconsistencySpan.style.backgroundColor = 'rgba(245, 158, 11, 0.1)';
              inconsistencySpan.style.borderRadius = '2px';
              inconsistencySpan.style.animationDuration = '1s';
            });
            
            inconsistencySpan.addEventListener('mouseleave', () => {
              inconsistencySpan.style.backgroundColor = 'transparent';
              inconsistencySpan.style.borderRadius = '0';
              inconsistencySpan.style.animationDuration = '2s';
            });
            
            inconsistencySpan.textContent = highlightText;
            
            // Replace the text node with our highlighted version
            const parent = textNode.parentNode;
            if (parent) {
              if (beforeText) {
                parent.insertBefore(document.createTextNode(beforeText), textNode);
              }
              parent.insertBefore(inconsistencySpan, textNode);
              if (afterText) {
                parent.insertBefore(document.createTextNode(afterText), textNode);
              }
              parent.removeChild(textNode);
              
              console.log('✅ Applied voice inconsistency underline to:', highlightText.substring(0, 50));
              console.log('🎨 Element classes:', inconsistencySpan.className);
              console.log('🎨 Element styles:', inconsistencySpan.style.cssText);
              console.log('🎨 Animation style:', inconsistencySpan.style.animation);
            }
            break;
          }
          
          currentOffset += nodeLength;
        }
      }
    });
  }, [editor]);

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
    if (editor && contentProp !== undefined) {
      const currentContent = editor.getHTML();
      const currentText = editor.getText();
      
      // Handle both HTML and plain text content
      const isContentDifferent = currentContent !== contentProp && currentText !== contentProp;
      
      if (isContentDifferent) {
        console.log('🔄 Updating editor content:', {
          currentContentLength: currentContent.length,
          currentTextLength: currentText.length,
          newContentLength: contentProp.length,
          newContentPreview: contentProp.substring(0, 100) + '...',
          isHTML: contentProp.includes('<') && contentProp.includes('>')
        });
        
        // Set content and preserve cursor position if possible
        const { from } = editor.state.selection;
        editor.commands.setContent(contentProp);
        
        // Try to restore cursor position or focus at the end
        try {
          if (from <= editor.state.doc.content.size) {
            editor.commands.setTextSelection(from);
          } else {
            editor.commands.focus('end');
          }
        } catch (error) {
          // If cursor positioning fails, just focus at the end
          console.warn('Failed to restore cursor position:', error);
          editor.commands.focus('end');
        }
      }
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
      
      {/* Voice consistency indicator */}
      {(() => {
        const inconsistentResults = voiceConsistencyResults.filter(r => !r.is_consistent);
        const hasVoiceIssues = inconsistentResults.length > 0;
        
        if (!hasVoiceIssues) return null;
        
        return (
          <div className="voice-consistency-indicator" style={{
            position: 'fixed',
            bottom: '20px',
            right: '20px',
            background: '#ff6b35',
            color: 'white',
            padding: '8px 12px',
            borderRadius: '8px',
            fontSize: '12px',
            zIndex: 1000,
            boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)',
            display: 'flex',
            alignItems: 'center',
            gap: '6px'
          }}>
            <span>💬</span>
            <span>
              {inconsistentResults.length === 1 
                ? `1 character voice issue` 
                : `${inconsistentResults.length} character voice issues`}
            </span>
          </div>
        );
      })()}
    </div>
  );
};

export default HighlightableEditor; 