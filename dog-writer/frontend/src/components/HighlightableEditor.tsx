import { useEditor, EditorContent } from '@tiptap/react';
import StarterKit from '@tiptap/starter-kit';
import Highlight from '@tiptap/extension-highlight';
import { Mark } from '@tiptap/core';
import React, { useCallback, useEffect, useState, forwardRef } from 'react';
import { useAppContext } from '../contexts/AppContext';
import '../styles/highlightable-editor.css';

// Custom highlight extension with multiple colors
const CustomHighlight = Mark.create({
  name: 'customHighlight',
  
  addOptions() {
    return {
      multicolor: true,
      HTMLAttributes: {},
    }
  },

  addAttributes() {
    return {
      color: {
        default: 'feedback-request',
        parseHTML: element => element.getAttribute('data-color'),
        renderHTML: attributes => {
          if (!attributes.color) {
            return {}
          }
          return { 'data-color': attributes.color, class: `highlight-${attributes.color}` }
        },
      },
      id: {
        default: null,
        parseHTML: element => element.getAttribute('data-highlight-id'),
        renderHTML: attributes => {
          if (!attributes.id) {
            return {}
          }
          return { 'data-highlight-id': attributes.id }
        },
      },
    }
  },

  parseHTML() {
    return [
      {
        tag: 'mark[data-color]',
      },
    ]
  },

  renderHTML({ HTMLAttributes }) {
    return ['mark', HTMLAttributes, 0]
  },

  addCommands() {
    return {
      setHighlight:
        (attributes) =>
        ({ commands }) => {
          return commands.setMark(this.name, attributes)
        },
      toggleHighlight:
        (attributes) =>
        ({ commands }) => {
          return commands.toggleMark(this.name, attributes)
        },
      unsetHighlight:
        () =>
        ({ commands }) => {
          return commands.unsetMark(this.name)
        },
    }
  },
})

interface HighlightableEditorProps {
  content?: string;
  onChange?: (content: string) => void;
  onTextHighlighted?: (text: string, highlightId: string) => void;
  onHighlightRemoved?: (highlightId: string) => void;
}

interface HighlightInfo {
  id: string;
  text: string;
  color: string;
  position: { from: number; to: number };
  timestamp: number;
}

const HighlightableEditor = forwardRef<HTMLDivElement, HighlightableEditorProps>(({ 
  content: contentProp, 
  onChange: onChangeProp, 
  onTextHighlighted: onTextHighlightedProp,
  onHighlightRemoved: onHighlightRemovedProp
}, ref) => {
  // Use context values as fallback if props are not provided
  const { 
    editorContent: contextContent, 
    setEditorContent: contextOnChange,
    handleTextHighlighted: contextOnTextHighlighted
  } = useAppContext();

  // Use props if provided, otherwise use context
  const content = contentProp !== undefined ? contentProp : contextContent;
  const onChange = onChangeProp || contextOnChange;
  const onTextHighlighted = onTextHighlightedProp || contextOnTextHighlighted;
  const onHighlightRemoved = onHighlightRemovedProp || (() => {});

  const [highlights, setHighlights] = useState<HighlightInfo[]>([]);
  const [showHighlightTooltip, setShowHighlightTooltip] = useState(false);
  const [tooltipPosition, setTooltipPosition] = useState({ x: 0, y: 0 });
  const [selectedText, setSelectedText] = useState('');
  const [isSelecting, setIsSelecting] = useState(false);

  const editor = useEditor({
    extensions: [
      StarterKit,
      CustomHighlight.configure({
        multicolor: true,
      }),
    ],
    content: content || '',
    onUpdate: ({ editor }) => {
      const newContent = editor.getHTML();
      onChange(newContent);
    },
    onSelectionUpdate: ({ editor }) => {
      const { from, to } = editor.state.selection;
      const selectedText = editor.state.doc.textBetween(from, to, ' ');
      
      if (selectedText.trim() && selectedText.length > 2) {
        setSelectedText(selectedText.trim());
        setIsSelecting(true);
        
        // Get the position of the selection for tooltip placement
        const coords = editor.view.coordsAtPos(from);
        setTooltipPosition({
          x: coords.left,
          y: coords.top - 60, // Position above the selection
        });
        setShowHighlightTooltip(true);
      } else {
        setShowHighlightTooltip(false);
        setIsSelecting(false);
        setSelectedText('');
      }
    },
  });

  // Function to create a highlight for feedback
  const createHighlight = useCallback((color: string = 'feedback-request') => {
    if (!editor || !selectedText) return;

    const highlightId = `highlight-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
    const { from, to } = editor.state.selection;

    // Apply the highlight
    editor.chain().focus().setHighlight({ 
      color, 
      id: highlightId 
    }).run();

    // Store highlight info
    const highlightInfo: HighlightInfo = {
      id: highlightId,
      text: selectedText,
      color,
      position: { from, to },
      timestamp: Date.now(),
    };

    setHighlights(prev => [...prev, highlightInfo]);

    // Notify parent component with highlight type
    onTextHighlighted(selectedText, highlightId);

    // Hide tooltip and clear selection
    setShowHighlightTooltip(false);
    setIsSelecting(false);
    setSelectedText('');

    // Clear the text selection
    editor.commands.setTextSelection(to);
  }, [editor, selectedText, onTextHighlighted]);

  // Function to create highlight and send to chat with specific request type
  const createHighlightAndSendToChat = useCallback((color: string, requestType: string) => {
    if (!editor || !selectedText) return;

    const highlightId = `highlight-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
    const { from, to } = editor.state.selection;

    // Apply the highlight
    editor.chain().focus().setHighlight({ 
      color, 
      id: highlightId 
    }).run();

    // Store highlight info
    const highlightInfo: HighlightInfo = {
      id: highlightId,
      text: selectedText,
      color,
      position: { from, to },
      timestamp: Date.now(),
    };

    setHighlights(prev => [...prev, highlightInfo]);

    // Notify parent component with the highlighted text and request type
    onTextHighlighted(selectedText, highlightId);

    // Hide tooltip and clear selection
    setShowHighlightTooltip(false);
    setIsSelecting(false);
    setSelectedText('');

    // Clear the text selection
    editor.commands.setTextSelection(to);

    // Trigger chat with specific request
    // This will be handled by the parent component (App.tsx) to open chat and send message
    const event = new CustomEvent('highlightedTextForChat', {
      detail: {
        text: selectedText,
        requestType,
        highlightId,
        color
      }
    });
    window.dispatchEvent(event);
  }, [editor, selectedText, onTextHighlighted]);

  // Improved tooltip positioning to avoid covering text
  const getTooltipPosition = useCallback((coords: { left: number; top: number }) => {
    const tooltip = document.querySelector('.highlight-tooltip') as HTMLElement;
    if (!tooltip) return { x: coords.left, y: coords.top - 60 };

    const tooltipRect = tooltip.getBoundingClientRect();
    const viewportWidth = window.innerWidth;
    const viewportHeight = window.innerHeight;

    let x = coords.left;
    let y = coords.top - 60; // Default: above selection

    // Adjust horizontal position if tooltip would go off-screen
    if (x + tooltipRect.width > viewportWidth - 20) {
      x = viewportWidth - tooltipRect.width - 20;
    }
    if (x < 20) {
      x = 20;
    }

    // If tooltip would go above viewport, position it below the selection
    if (y < 20) {
      y = coords.top + 30; // Below selection
    }

    // If still off-screen, position to the side
    if (y + tooltipRect.height > viewportHeight - 20) {
      y = coords.top - tooltipRect.height / 2;
      x = coords.left + 100; // To the right
      
      // If right side is off-screen, try left side
      if (x + tooltipRect.width > viewportWidth - 20) {
        x = coords.left - tooltipRect.width - 20; // To the left
      }
    }

    return { x, y };
  }, []);

  // Update selection handler to use improved positioning
  useEffect(() => {
    if (!editor) return;

    const handleSelectionUpdate = () => {
      const { from, to } = editor.state.selection;
      const selectedText = editor.state.doc.textBetween(from, to, ' ');
      
      if (selectedText.trim() && selectedText.length > 2) {
        setSelectedText(selectedText.trim());
        setIsSelecting(true);
        
        // Get the position of the selection for tooltip placement
        const coords = editor.view.coordsAtPos(from);
        const improvedPosition = getTooltipPosition(coords);
        
        setTooltipPosition({
          x: improvedPosition.x,
          y: improvedPosition.y,
        });
        setShowHighlightTooltip(true);
      } else {
        setShowHighlightTooltip(false);
        setIsSelecting(false);
        setSelectedText('');
      }
    };

    // Replace the existing onSelectionUpdate in editor configuration
    editor.on('selectionUpdate', handleSelectionUpdate);

    return () => {
      editor.off('selectionUpdate', handleSelectionUpdate);
    };
  }, [editor, getTooltipPosition]);

  // Function to remove a highlight
  const removeHighlight = useCallback((highlightId: string) => {
    if (!editor) return;

    // Find the highlight
    const highlight = highlights.find(h => h.id === highlightId);
    if (!highlight) return;

    // Remove the highlight from the editor
    const { from, to } = highlight.position;
    editor.chain().focus().setTextSelection({ from, to }).unsetHighlight().run();

    // Remove from our highlights array
    setHighlights(prev => prev.filter(h => h.id !== highlightId));

    // Notify parent component
    onHighlightRemoved(highlightId);
  }, [editor, highlights, onHighlightRemoved]);

  // Handle clicking on existing highlights
  useEffect(() => {
    if (!editor) return;

    const handleClick = (event: MouseEvent) => {
      const target = event.target as HTMLElement;
      const highlightElement = target.closest('[data-highlight-id]');
      
      if (highlightElement) {
        const highlightId = highlightElement.getAttribute('data-highlight-id');
        if (highlightId) {
          // Show context menu or highlight info
          console.log('Clicked highlight:', highlightId);
        }
      }
    };

    const editorElement = editor.view.dom;
    editorElement.addEventListener('click', handleClick);

    return () => {
      editorElement.removeEventListener('click', handleClick);
    };
  }, [editor]);

  // Update editor content when the content prop changes
  useEffect(() => {
    if (editor && content && editor.getHTML() !== content) {
      editor.commands.setContent(content);
    }
  }, [content, editor]);

  // Auto-hide tooltip after 5 seconds of no interaction
  useEffect(() => {
    if (showHighlightTooltip) {
      const timer = setTimeout(() => {
        setShowHighlightTooltip(false);
        setIsSelecting(false);
      }, 5000);

      return () => clearTimeout(timer);
    }
  }, [showHighlightTooltip]);

  return (
    <div className="highlightable-editor-container" ref={ref}>
      <div className="editor-wrapper">
        <EditorContent 
          editor={editor} 
          className="highlightable-editor"
        />
        
        {/* Highlight Tooltip */}
        {showHighlightTooltip && isSelecting && (
          <div 
            className="highlight-tooltip"
            style={{
              position: 'fixed',
              left: `${tooltipPosition.x}px`,
              top: `${tooltipPosition.y}px`,
              zIndex: 1000,
            }}
          >
            <div className="highlight-tooltip-content">
              <div className="highlight-tooltip-text">
                Get AI feedback on: "{selectedText.length > 50 ? selectedText.substring(0, 50) + '...' : selectedText}"
              </div>
              <div className="highlight-tooltip-actions">
                <button
                  className="highlight-btn highlight-btn-primary"
                  onClick={() => createHighlightAndSendToChat('feedback-request', 'feedback')}
                >
                  🔍 Get Feedback
                </button>
                <button
                  className="highlight-btn highlight-btn-secondary"
                  onClick={() => createHighlightAndSendToChat('improvement', 'improve')}
                >
                  ✨ Improve This
                </button>
                <button
                  className="highlight-btn highlight-btn-tertiary"
                  onClick={() => createHighlightAndSendToChat('question', 'question')}
                >
                  ❓ Ask Question
                </button>
                <button
                  className="highlight-btn highlight-btn-cancel"
                  onClick={() => {
                    setShowHighlightTooltip(false);
                    setIsSelecting(false);
                  }}
                >
                  ✕
                </button>
              </div>
            </div>
          </div>
        )}
        
        {/* Highlights Sidebar */}
        {highlights.length > 0 && (
          <div className="highlights-sidebar">
            <div className="highlights-header">
              <h3>📝 Highlighted for Feedback</h3>
              <span className="highlights-count">{highlights.length}</span>
            </div>
            <div className="highlights-list">
              {highlights.map((highlight) => (
                <div key={highlight.id} className={`highlight-item highlight-${highlight.color}`}>
                  <div className="highlight-item-text">
                    {highlight.text.length > 100 
                      ? highlight.text.substring(0, 100) + '...' 
                      : highlight.text
                    }
                  </div>
                  <div className="highlight-item-meta">
                    <span className="highlight-type">
                      {highlight.color === 'feedback-request' && '🔍 Feedback'}
                      {highlight.color === 'improvement' && '✨ Improve'}
                      {highlight.color === 'question' && '❓ Question'}
                    </span>
                    <button
                      className="highlight-remove-btn"
                      onClick={() => removeHighlight(highlight.id)}
                      title="Remove highlight"
                    >
                      ✕
                    </button>
                  </div>
                </div>
              ))}
            </div>
            <div className="highlights-actions">
              <button
                className="clear-all-highlights-btn"
                onClick={() => {
                  highlights.forEach(h => removeHighlight(h.id));
                }}
              >
                Clear All Highlights
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
});

HighlightableEditor.displayName = 'HighlightableEditor';

export default HighlightableEditor; 