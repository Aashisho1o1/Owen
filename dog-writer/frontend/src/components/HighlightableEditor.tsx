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

    // Notify parent component
    onTextHighlighted(selectedText, highlightId);

    // Hide tooltip and clear selection
    setShowHighlightTooltip(false);
    setIsSelecting(false);
    setSelectedText('');

    // Clear the text selection
    editor.commands.setTextSelection(to);
  }, [editor, selectedText, onTextHighlighted]);

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
                  onClick={() => createHighlight('feedback-request')}
                >
                  🔍 Get Feedback
                </button>
                <button
                  className="highlight-btn highlight-btn-secondary"
                  onClick={() => createHighlight('improvement')}
                >
                  ✨ Improve This
                </button>
                <button
                  className="highlight-btn highlight-btn-tertiary"
                  onClick={() => createHighlight('question')}
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