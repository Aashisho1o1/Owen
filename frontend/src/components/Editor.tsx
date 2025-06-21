import React, { useEffect, useRef, useState, useCallback } from 'react';
import { EditorView, keymap, placeholder } from '@codemirror/view';
import { EditorState } from '@codemirror/state';
import { useEditorContext } from '../contexts/EditorContext';
import { useChatContext } from '../contexts/ChatContext';
import '../styles/editor.css';

interface EditorProps {
  content?: string;
  onChange?: (content: string) => void;
  onTextHighlighted?: (text: string) => void;
}

const Editor: React.FC<EditorProps> = ({ 
  content, 
  onChange, 
  onTextHighlighted 
}) => {
  const { 
    editorContent, 
    setEditorContent,
    handleSaveCheckpoint
  } = useEditorContext();
  
  const {
    handleTextHighlighted,
    clearTextHighlight
  } = useChatContext();

  const [fontSize, setFontSize] = useState('16px');
  const [fontFamily, setFontFamily] = useState('Inter');
  
  // Grammar checking state - restored but simplified
  const [grammarIssues, setGrammarIssues] = useState<any[]>([]); // Changed from GrammarIssue[] to any[] as GrammarIssue is removed
  const [isCheckingGrammar, setIsCheckingGrammar] = useState(false);
  const [hoveredIssue, setHoveredIssue] = useState<any | null>(null); // Changed from GrammarIssue | null to any | null
  const [tooltipPosition, setTooltipPosition] = useState({ x: 0, y: 0 });
  
  const editor = useEditor({
    extensions: [
      StarterKit,
      Paragraph,
    ],
    content: content || '',
    onUpdate: ({ editor }) => {
      const newContent = editor.getHTML();
      onChange(newContent);
      
      // Subtle grammar checking on content change
      handleGrammarCheck(editor.getText());
    },
  });

  // Grammar checking function - restored
  const handleGrammarCheck = useCallback((text: string) => {
    if (!text.trim() || text.length < 10) {
      setGrammarIssues([]);
      return;
    }
    
    setIsCheckingGrammar(true);
    
    grammarService.checkRealTimeDebounced(text, (result: any) => { // Changed from GrammarCheckResult to any
      setGrammarIssues(result.issues);
      setIsCheckingGrammar(false);
    });
  }, []);

  // Apply grammar suggestion
  const applySuggestion = useCallback((issue: any, suggestion: string) => { // Changed from GrammarIssue to any
    if (!editor) return;
    
    const currentText = editor.getText();
    const beforeText = currentText.substring(0, issue.start);
    const afterText = currentText.substring(issue.end);
    const newText = beforeText + suggestion + afterText;
    
    editor.commands.setContent(newText);
    setGrammarIssues(prev => prev.filter(i => i !== issue));
    setHoveredIssue(null);
  }, [editor]);

  // Handle mouse events for grammar highlighting
  useEffect(() => {
    if (!editor) return;

    const editorElement = editor.view.dom;
    
    const handleMouseMove = (e: MouseEvent) => {
      const rect = editorElement.getBoundingClientRect();
      const x = e.clientX - rect.left;
      const y = e.clientY - rect.top;
      
      // Find if cursor is over a grammar issue
      const hoveredElement = e.target as HTMLElement;
      if (hoveredElement.classList.contains('grammar-error')) {
        const issueIndex = parseInt(hoveredElement.dataset.issueIndex || '0');
        const issue = grammarIssues[issueIndex];
        if (issue) {
          setHoveredIssue(issue);
          setTooltipPosition({ x: e.clientX, y: e.clientY });
        }
      } else {
        setHoveredIssue(null);
      }
    };

    const handleMouseLeave = () => {
      setHoveredIssue(null);
    };

    editorElement.addEventListener('mousemove', handleMouseMove);
    editorElement.addEventListener('mouseleave', handleMouseLeave);

    return () => {
      editorElement.removeEventListener('mousemove', handleMouseMove);
      editorElement.removeEventListener('mouseleave', handleMouseLeave);
    };
  }, [editor, grammarIssues]);

  // Apply grammar highlighting to the editor content
  useEffect(() => {
    if (!editor || grammarIssues.length === 0) return;

    const editorText = editor.getText();
    let highlightedHTML = editorText;

    // Sort issues by start position (reverse order to maintain positions)
    const sortedIssues = [...grammarIssues].sort((a, b) => b.start - a.start);

    sortedIssues.forEach((issue, index) => {
      const beforeText = highlightedHTML.substring(0, issue.start);
      const issueText = highlightedHTML.substring(issue.start, issue.end);
      const afterText = highlightedHTML.substring(issue.end);

      const severityClass = `grammar-${issue.severity}`;
      const wrappedText = `<span class="grammar-error ${severityClass}" data-issue-index="${grammarIssues.indexOf(issue)}">${issueText}</span>`;
      
      highlightedHTML = beforeText + wrappedText + afterText;
    });

    // Only update if content has changed
    if (editor.getHTML() !== highlightedHTML) {
      const currentSelection = editor.state.selection;
      editor.commands.setContent(highlightedHTML, false);
      // Restore selection if possible
      try {
        editor.commands.setTextSelection(currentSelection);
      } catch (e) {
        // Selection restoration failed, that's ok
      }
    }
  }, [grammarIssues, editor]);

  // Update editor content when the content prop changes
  useEffect(() => {
    if (editor && content && editor.getHTML() !== content) {
      editor.commands.setContent(content);
    }
  }, [content, editor]);
  
  // Set up placeholder effect
  useEffect(() => {
    if (editor && editor.isEmpty) {
      document.querySelector('.ProseMirror')?.classList.add('is-empty');
    }
  }, [editor]);
  
  // Handle text selection
  const handleSelectionChange = useCallback(() => {
    if (editor && editor.view.state.selection.content().size > 0) {
      const { from, to } = editor.view.state.selection;
      const selectedText = editor.view.state.doc.textBetween(from, to, ' ');
      if (selectedText.trim()) {
        // Clear any previous highlighting
        clearSelectedTextHighlight();
        
        // Add visual feedback for selected text
        addSelectedTextHighlight(from, to);
        
        onTextHighlighted(selectedText);
        
        // Auto-clear selection highlighting after 5 seconds
        setTimeout(() => {
          clearSelectedTextHighlight();
        }, 5000);
      }
    } else {
      // Clear highlighting when selection is cleared
      clearSelectedTextHighlight();
    }
  }, [editor, onTextHighlighted]);

  // Function to add visual highlight to selected text
  const addSelectedTextHighlight = useCallback((from: number, to: number) => {
    if (!editor) return;
    
    try {
      const editorElement = editor.view.dom;
      const selection = editor.view.state.selection;
      
      // Create a temporary class to highlight the selected text
      const currentHTML = editor.getHTML();
      const beforeText = editor.view.state.doc.textBetween(0, from, ' ');
      const selectedText = editor.view.state.doc.textBetween(from, to, ' ');
      const afterText = editor.view.state.doc.textBetween(to, editor.view.state.doc.content.size, ' ');
      
      const highlightedHTML = beforeText + 
        `<span class="text-selected-for-ai">${selectedText}</span>` + 
        afterText;
      
      // Update content while preserving cursor position
      editor.commands.setContent(highlightedHTML, false);
    } catch (error) {
      console.warn('Could not add visual highlight:', error);
    }
  }, [editor]);

  // Function to clear visual highlight
  const clearSelectedTextHighlight = useCallback(() => {
    if (!editor) return;
    
    try {
      const editorElement = editor.view.dom;
      const highlightedElements = editorElement.querySelectorAll('.text-selected-for-ai');
      
      highlightedElements.forEach(element => {
        const parent = element.parentNode;
        if (parent) {
          parent.insertBefore(document.createTextNode(element.textContent || ''), element);
          parent.removeChild(element);
        }
      });
    } catch (error) {
      console.warn('Could not clear visual highlight:', error);
    }
  }, [editor]);
  
  // Apply font size and family
  useEffect(() => {
    const editorElement = document.querySelector('.ProseMirror');
    if (editorElement) {
      editorElement.setAttribute('style', `font-size: ${fontSize}; font-family: ${fontFamily}, var(--font-sans);`);
    }
  }, [fontSize, fontFamily, editor]);
  
  // Add event listener for selection changes
  React.useEffect(() => {
    if (!editor) return;
    
    const onSelectionUpdate = () => {
      handleSelectionChange();
    };

    // Handle mouseup events for better selection detection
    const handleMouseUp = () => {
      setTimeout(() => {
        handleSelectionChange();
      }, 10); // Small delay to ensure selection is finalized
    };

    // Handle keyboard selection (Shift + arrow keys)
    const handleKeyUp = (e: KeyboardEvent) => {
      if (e.shiftKey || e.key === 'ArrowLeft' || e.key === 'ArrowRight' || e.key === 'ArrowUp' || e.key === 'ArrowDown') {
        setTimeout(() => {
          handleSelectionChange();
        }, 10);
      }
    };
    
    editor.on('selectionUpdate', onSelectionUpdate);
    
    // Add direct DOM event listeners for better selection detection
    const editorElement = editor.view.dom;
    editorElement.addEventListener('mouseup', handleMouseUp);
    editorElement.addEventListener('keyup', handleKeyUp);
    
    // Handle focus/blur for placeholder
    const handleTransaction = () => {
      const editorElement = document.querySelector('.ProseMirror');
      if (editor.isEmpty) {
        editorElement?.classList.add('is-empty');
      } else {
        editorElement?.classList.remove('is-empty');
      }
    };
    
    editor.on('transaction', handleTransaction);
    
    return () => {
      editor.off('selectionUpdate', onSelectionUpdate);
      editor.off('transaction', handleTransaction);
      editorElement.removeEventListener('mouseup', handleMouseUp);
      editorElement.removeEventListener('keyup', handleKeyUp);
    };
  }, [editor, handleSelectionChange]);

  return (
    <div className="editor-container">
      <div className="editor-header">
        <h2>Text Content</h2>
        <p className="selection-hint">
          Highlight text to discuss with the AI
          {isCheckingGrammar && <span className="grammar-checking"> • Checking grammar...</span>}
        </p>
      </div>
      
      <div className="editor-content">
        <EditorContent editor={editor} />
      </div>

      {/* Grammar Tooltip - appears on hover */}
      {hoveredIssue && (
        <div ref={tooltipRef} className="grammar-tooltip" style={tooltipStyle}>
          <div className="tooltip-content">
            <div className="tooltip-message">{hoveredIssue.message}</div>
            {hoveredIssue.suggestions && hoveredIssue.suggestions.length > 0 && (
              <div className="tooltip-suggestions">
                {hoveredIssue.suggestions.map((suggestion, index) => (
                  <button
                    key={index}
                    className="suggestion-button"
                    onClick={() => handleSuggestionClick(suggestion.value)}
                  >
                    {suggestion.value}
                  </button>
                ))}
              </div>
            )}
            <div className="tooltip-source">{hoveredIssue.source}</div>
          </div>
        </div>
      )}
    </div>
  );
});

Editor.displayName = 'Editor';

export default Editor; 