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
import { VoiceInconsistencyMark } from '../extensions/VoiceInconsistencyMark';
import { HighlightDecorations } from '../extensions/HighlightDecorations';

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
  const { voiceGuardEnabled } = useChatContext();

  // Use props if provided, otherwise use context
  const contentProp = content !== undefined ? content : contextContent;
  const onChangeProp = onChange || contextOnChange;

  // Content tracking (removed console logs for production)

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
  
  // Add observer to maintain voice inconsistency styles
  const voiceInconsistencyObserver = useRef<MutationObserver | null>(null);
  
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
  
  // Add debounce ref for content updates
  const updateDebounceRef = useRef<NodeJS.Timeout | null>(null);
  
  const editor = useEditor({
    extensions: [
      StarterKit,
      VoiceInconsistencyMark,
      HighlightDecorations,
    ],
    content: contentProp || '',
    onUpdate: async ({ editor }) => {
      const newContent = editor.getHTML();
      
      // Debounce content updates to prevent excessive saves
      if (updateDebounceRef.current) {
        clearTimeout(updateDebounceRef.current);
      }
      
      // Update content immediately for responsive UI
      updateDebounceRef.current = setTimeout(() => {
        onChangeProp(newContent);
      }, 300); // 300ms debounce for optimal UX
      
      // Only run voice analysis for authenticated users with sufficient content
      // CONDITIONAL LOGIC: Only run voice analysis if VoiceGuard is enabled
      if (isAuthenticated && voiceGuardEnabled && newContent && newContent.trim().length > 50) {
        try {
          // Get plain text for voice analysis (not HTML)
          const plainText = editor.getText();
          const response = await analyzeVoiceConsistency(plainText);
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

  // Enhanced fuzzy text matching function
  const findBestTextMatch = (nodeText: string, flaggedText: string) => {
    const nodeTextLower = nodeText.toLowerCase();
    const flaggedTextLower = flaggedText.toLowerCase();
    
    // Strategy 1: Direct match
    let matchIndex = nodeTextLower.indexOf(flaggedTextLower);
    if (matchIndex !== -1) {
      return { index: matchIndex, length: flaggedTextLower.length };
    }
    
    // Strategy 2: Clean text by removing quotes and punctuation
    const cleanFlagged = flaggedTextLower.replace(/["""''`"'()[\]]/g, '').replace(/\s+/g, ' ').trim();
    const cleanNode = nodeTextLower.replace(/["""''`"'()[\]]/g, '').replace(/\s+/g, ' ');
    
    matchIndex = cleanNode.indexOf(cleanFlagged);
    if (matchIndex !== -1 && cleanFlagged.length > 3) {
      // Find the original position by counting characters
      let originalIndex = 0;
      let cleanIndex = 0;
      while (cleanIndex < matchIndex && originalIndex < nodeText.length) {
        if (!/["""''`"'()[\]]/.test(nodeText[originalIndex])) {
          cleanIndex++;
        }
        originalIndex++;
      }
      return { index: originalIndex, length: cleanFlagged.length + 2 }; // Add some buffer
    }
    
    // Strategy 3: Extract core words and find partial matches
    const flaggedWords = cleanFlagged.split(' ').filter(word => word.length > 2);
    if (flaggedWords.length > 0) {
      const firstWord = flaggedWords[0];
      const lastWord = flaggedWords[flaggedWords.length - 1];
      
      const firstWordIndex = cleanNode.indexOf(firstWord);
      const lastWordIndex = cleanNode.indexOf(lastWord, firstWordIndex);
      
      if (firstWordIndex !== -1 && lastWordIndex !== -1) {
        // Map back to original text
        let originalStart = 0;
        let cleanPos = 0;
        while (cleanPos < firstWordIndex && originalStart < nodeText.length) {
          if (!/["""''`"'()[\]]/.test(nodeText[originalStart])) {
            cleanPos++;
          }
          originalStart++;
        }
        const estimatedLength = Math.max(flaggedText.length, lastWordIndex - firstWordIndex + lastWord.length);
        return { index: originalStart, length: estimatedLength };
      }
    }
    
    // Strategy 4: Fuzzy word matching - find any significant words
    if (flaggedWords.length > 0) {
      for (const word of flaggedWords) {
        if (word.length > 4) { // Only match significant words
          const wordIndex = nodeTextLower.indexOf(word);
          if (wordIndex !== -1) {
            return { index: wordIndex, length: Math.min(flaggedText.length, word.length + 10) };
          }
        }
      }
    }
    
    return null;
  };

  const applyVoiceInconsistencyUnderlines = (results: VoiceConsistencyResult[]) => {
    if (!editor) return;

    const doc = editor.state.doc;
    const tr = editor.state.tr;
    let appliedCount = 0;

    results.forEach((result) => {
      // ENHANCED: Apply underlines for inconsistent OR low-confidence results (or all in debug mode)
      const shouldHighlight = !result.is_consistent || result.confidence_score < 0.7;
      
      if (shouldHighlight) {
        const textToFind = result.flagged_text;
        console.log(`🔍 Looking for text to highlight: "${textToFind}" (consistent: ${result.is_consistent}, confidence: ${result.confidence_score})`);

        let found = false;
        doc.descendants((node, pos) => {
          if (found || node.type.name !== 'text') return;

          const nodeText = node.text || '';
          
          // Use enhanced fuzzy matching
          const match = findBestTextMatch(nodeText, textToFind);
          
          if (match) {
            const from = pos + match.index;
            const to = Math.min(pos + match.index + match.length, pos + nodeText.length);
            
            console.log(`✅ Found match at position ${from}-${to}:`, nodeText.slice(match.index, match.index + match.length));
            
            // Use orange for low confidence, red for inconsistent, blue for debug mode
            const confidenceLevel = !result.is_consistent ? 'high' : 
                                   result.confidence_score < 0.5 ? 'high' :
                                   result.confidence_score < 0.7 ? 'medium' : 'low';
            
            tr.addMark(from, to, editor.schema.marks.voiceInconsistency.create({
              character: result.character_name,
              confidence: result.confidence_score,
              explanation: result.explanation,
              confidenceLevel: confidenceLevel
            }));
            
            appliedCount++;
            found = true;
          }
        });

        if (!found) {
          console.warn(`❌ Could not find text for character: ${result.character_name} text: '${textToFind}'`);
        }
      }
    });

    if (tr.docChanged) {
      editor.view.dispatch(tr);
      console.log(`✅ Applied ${appliedCount} voice inconsistency underlines`);
    } else {
      console.log(`ℹ️ No underlines applied - all ${results.length} characters appear consistent (confidence > 0.7)`);
      
      // DEBUGGING: Show toast notification when analysis completes but no issues found
      if (results.length > 0) {
        const avgConfidence = results.reduce((sum, r) => sum + r.confidence_score, 0) / results.length;
        console.log(`🎯 Analysis Summary: ${results.length} characters analyzed, average confidence: ${avgConfidence.toFixed(2)}`);
        
        // Temporary visual feedback for successful analysis with no issues
        const notification = document.createElement('div');
        notification.style.cssText = `
          position: fixed;
          top: 20px;
          right: 20px;
          background: #10B981;
          color: white;
          padding: 12px 16px;
          border-radius: 8px;
          z-index: 10000;
          font-size: 14px;
          box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        `;
        notification.textContent = `✅ Voice analysis complete: ${results.length} characters consistent`;
        document.body.appendChild(notification);
        
        setTimeout(() => {
          if (notification.parentNode) {
            notification.parentNode.removeChild(notification);
          }
        }, 3000);
      }
    }
  };

  // Handle active discussion highlighting using Tiptap decorations (survives re-renders)
  useEffect(() => {
    let isMounted = true; // MEMORY LEAK FIX: Track component mount state
    
    const handleActiveDiscussionHighlight = (event: CustomEvent) => {
      if (!editor || !isMounted) return; // MEMORY LEAK FIX: Check if component is still mounted

      const { text, action, highlightId } = event.detail;
      
      console.log('🎯 DECORATION HIGHLIGHT EVENT:', { text, action, highlightId, hasEditor: !!editor });
      
      if (action === 'add' && text) {
        // Use decoration-based highlighting instead of DOM manipulation
        const id = highlightId || `highlight-${Date.now()}`;
        console.log('✨ Adding decoration-based highlight:', text);
        
        // Add the new highlight using our decoration extension (don't clear first)
        const success = editor.commands.addHighlight({
          id,
          text,
          className: 'active-discussion-highlight'
        });
        
        if (success) {
          console.log('✅ Decoration highlight applied successfully:', text);
        } else {
          console.warn('⚠️ Failed to apply decoration highlight:', text);
        }
        
      } else if (action === 'remove') {
        // Remove specific highlight by ID
        const id = highlightId || 'unknown';
        console.log('🧹 Removing decoration highlight:', id);
        editor.commands.removeHighlight(id);
        
      } else if (action === 'clear-all') {
        // Clear all highlights using decoration commands
        console.log('🧹 CLEAR-ALL: Removing all decoration highlights');
        editor.commands.clearAllHighlights();
      }
    };

    window.addEventListener('applyActiveDiscussionHighlight', handleActiveDiscussionHighlight as EventListener);
    
    return () => {
      isMounted = false; // MEMORY LEAK FIX: Mark component as unmounted
      
      // Clean up voice inconsistency observer
      if (voiceInconsistencyObserver.current) {
        voiceInconsistencyObserver.current.disconnect();
        voiceInconsistencyObserver.current = null;
      }
      
      // Clean up update debounce timer
      if (updateDebounceRef.current) {
        clearTimeout(updateDebounceRef.current);
        updateDebounceRef.current = null;
      }
      
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
      
      // CRITICAL FIX: Don't overwrite if user recently edited content
      const userHasRecentContent = currentContent.length > 0 && contentProp.length === 0;
      const shouldPreventOverwrite = userHasRecentContent && isContentDifferent;
      
      if (isContentDifferent && !shouldPreventOverwrite) {
        console.log('🔄 Updating editor content:', {
          currentContentLength: currentContent.length,
          currentTextLength: currentText.length,
          newContentLength: contentProp.length,
          newContentPreview: contentProp.substring(0, 100) + '...',
          isHTML: contentProp.includes('<') && contentProp.includes('>'),
          preventedOverwrite: false
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
      } else if (shouldPreventOverwrite) {
        console.log('🛡️ PREVENTING content overwrite to preserve user input:', {
          currentContentLength: currentContent.length,
          incomingContentLength: contentProp.length,
          reason: 'User has content, incoming is empty'
        });
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
        

        
        {/* Voice consistency indicator */}
        {(() => {
          // SAFETY: Ensure voiceConsistencyResults is defined before accessing
          if (!voiceConsistencyResults || !Array.isArray(voiceConsistencyResults)) {
            return null;
          }
          
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