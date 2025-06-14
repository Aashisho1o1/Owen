import { useEditor, EditorContent } from '@tiptap/react';
import StarterKit from '@tiptap/starter-kit';
import Paragraph from '@tiptap/extension-paragraph';
import React, { useCallback, useEffect, useState, forwardRef } from 'react';
import { useAppContext } from '../contexts/AppContext';
import { grammarService, GrammarIssue, GrammarCheckResult } from '../services/grammarService';
import { usePopper } from 'react-popper';
import { useAuth } from '../contexts/AuthContext';
import '../styles/editor.css';

interface EditorProps {
  content?: string;
  onChange?: (content: string) => void;
  onTextHighlighted?: (text: string) => void;
}

const Editor = forwardRef<HTMLDivElement, EditorProps>(({ 
  content: contentProp, 
  onChange: onChangeProp, 
  onTextHighlighted: onTextHighlightedProp 
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

  const [fontSize, setFontSize] = useState('16px');
  const [fontFamily, setFontFamily] = useState('Inter');
  
  // Grammar checking state - restored but simplified
  const [grammarIssues, setGrammarIssues] = useState<GrammarIssue[]>([]);
  const [isCheckingGrammar, setIsCheckingGrammar] = useState(false);
  const [hoveredIssue, setHoveredIssue] = useState<GrammarIssue | null>(null);
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
    
    grammarService.checkRealTimeDebounced(text, (result: GrammarCheckResult) => {
      setGrammarIssues(result.issues);
      setIsCheckingGrammar(false);
    });
  }, []);

  // Apply grammar suggestion
  const applySuggestion = useCallback((issue: GrammarIssue, suggestion: string) => {
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
        onTextHighlighted(selectedText);
      }
    }
  }, [editor, onTextHighlighted]);
  
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
    
    editor.on('selectionUpdate', onSelectionUpdate);
    
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
    };
  }, [editor, handleSelectionChange]);

  return (
    <div className="editor-container" ref={ref}>
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