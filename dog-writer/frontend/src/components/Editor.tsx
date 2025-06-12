import { useEditor, EditorContent } from '@tiptap/react';
import StarterKit from '@tiptap/starter-kit';
import Paragraph from '@tiptap/extension-paragraph';
import React, { useCallback, useEffect, useState, forwardRef } from 'react';
import { useAppContext } from '../contexts/AppContext';
import { grammarService, GrammarIssue, GrammarCheckResult } from '../services/grammarService';

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
        <div 
          className="grammar-tooltip"
          style={{
            position: 'fixed',
            left: tooltipPosition.x + 10,
            top: tooltipPosition.y - 10,
            zIndex: 1000
          }}
        >
          <div className="tooltip-content">
            <div className="tooltip-message">{hoveredIssue.message}</div>
            {hoveredIssue.suggestions.length > 0 && (
              <div className="tooltip-suggestions">
                {hoveredIssue.suggestions.slice(0, 3).map((suggestion, index) => (
                  <button
                    key={index}
                    className="suggestion-button"
                    onClick={() => applySuggestion(hoveredIssue, suggestion)}
                  >
                    {suggestion}
                  </button>
                ))}
              </div>
            )}
            <div className="tooltip-source">{hoveredIssue.source}</div>
          </div>
        </div>
      )}

      <style>{`
        .editor-container {
          display: flex;
          flex-direction: column;
          height: 100%;
          border-radius: var(--rounded-xl);
          overflow: hidden;
          background-color: var(--editor-bg);
          border: 1px solid var(--border-primary);
        }
        
        .editor-header {
          padding: 16px 20px;
          border-bottom: 1px solid var(--border-primary);
          background-color: var(--bg-secondary);
          display: flex;
          flex-direction: column;
          align-items: flex-start;
          gap: 8px;
        }
        
        .editor-header h2 {
          margin: 0;
          font-size: 1.125rem;
          font-weight: 600;
          color: var(--text-primary);
        }
        
        .selection-hint {
          margin: 0;
          font-size: 0.875rem;
          color: var(--text-secondary);
          font-style: italic;
        }
        
        .grammar-checking {
          color: var(--accent-blue);
          font-weight: 500;
        }
        
        .editor-content {
          flex: 1;
          padding: 20px;
          background-color: var(--editor-content-bg);
          overflow-y: auto;
        }
        
        .ProseMirror {
          outline: none;
          color: var(--text-primary);
          line-height: 1.6;
          min-height: 300px;
        }
        
        .ProseMirror.is-empty:before {
          color: var(--text-muted);
          content: "Start writing your story...";
          float: left;
          height: 0;
          pointer-events: none;
        }
        
        /* Grammar Error Highlighting - Subtle like Grammarly */
        .grammar-error {
          border-bottom: 2px dotted;
          cursor: pointer;
          position: relative;
        }
        
        .grammar-error.grammar-error {
          border-bottom-color: #ef4444;
        }
        
        .grammar-error.grammar-warning {
          border-bottom-color: #f59e0b;
        }
        
        .grammar-error.grammar-info {
          border-bottom-color: #3b82f6;
        }
        
        .grammar-error:hover {
          background-color: rgba(59, 130, 246, 0.1);
          border-radius: 2px;
        }
        
        /* Grammar Tooltip */
        .grammar-tooltip {
          background: var(--bg-primary);
          border: 1px solid var(--border-primary);
          border-radius: 8px;
          box-shadow: var(--shadow-lg);
          max-width: 300px;
          animation: fadeIn 0.2s ease-out;
        }
        
        .tooltip-content {
          padding: 12px;
        }
        
        .tooltip-message {
          font-size: 0.875rem;
          color: var(--text-primary);
          margin-bottom: 8px;
          line-height: 1.4;
        }
        
        .tooltip-suggestions {
          display: flex;
          flex-wrap: wrap;
          gap: 4px;
          margin-bottom: 8px;
        }
        
        .suggestion-button {
          padding: 4px 8px;
          background: var(--accent-blue);
          color: white;
          border: none;
          border-radius: 4px;
          font-size: 0.75rem;
          cursor: pointer;
          transition: all 0.2s;
        }
        
        .suggestion-button:hover {
          background: var(--accent-blue-hover);
        }
        
        .tooltip-source {
          font-size: 0.75rem;
          color: var(--text-muted);
          text-align: right;
          margin-top: 4px;
          border-top: 1px solid var(--border-light);
          padding-top: 4px;
        }
        
        .ProseMirror p {
          margin: 0 0 1em 0;
        }
        
        .ProseMirror h1,
        .ProseMirror h2,
        .ProseMirror h3,
        .ProseMirror h4,
        .ProseMirror h5,
        .ProseMirror h6 {
          color: var(--text-primary);
          margin: 1.5em 0 0.5em 0;
          font-weight: 600;
        }
        
        .ProseMirror h1 { font-size: 2em; }
        .ProseMirror h2 { font-size: 1.5em; }
        .ProseMirror h3 { font-size: 1.25em; }
        
        .ProseMirror ul,
        .ProseMirror ol {
          color: var(--text-primary);
          padding-left: 1.5em;
        }
        
        .ProseMirror li {
          margin: 0.25em 0;
        }
        
        .ProseMirror blockquote {
          border-left: 3px solid var(--accent-blue);
          padding-left: 1em;
          margin-left: 0;
          font-style: italic;
          color: var(--text-secondary);
        }
        
        .ProseMirror code {
          background-color: var(--bg-tertiary);
          color: var(--text-primary);
          padding: 0.2em 0.4em;
          border-radius: 3px;
          font-size: 0.9em;
        }
        
        .ProseMirror pre {
          background-color: var(--bg-tertiary);
          color: var(--text-primary);
          padding: 1em;
          border-radius: 6px;
          overflow-x: auto;
        }
        
        .ProseMirror pre code {
          background: none;
          padding: 0;
        }
        
        /* Selection highlighting */
        .ProseMirror ::selection {
          background-color: var(--accent-blue);
          color: white;
        }
        
        .ProseMirror::-moz-selection {
          background-color: var(--accent-blue);
          color: white;
        }
        
        /* Focus styles */
        .editor-container:focus-within {
          box-shadow: 0 0 0 2px var(--accent-blue);
        }
        
        /* Scrollbar styling */
        .editor-content::-webkit-scrollbar {
          width: 8px;
        }
        
        .editor-content::-webkit-scrollbar-track {
          background: var(--bg-secondary);
        }
        
        .editor-content::-webkit-scrollbar-thumb {
          background: var(--border-secondary);
          border-radius: 4px;
        }
        
        .editor-content::-webkit-scrollbar-thumb:hover {
          background: var(--text-muted);
        }
        
        @keyframes fadeIn {
          from { opacity: 0; transform: translateY(-4px); }
          to { opacity: 1; transform: translateY(0); }
        }
      `}</style>
    </div>
  );
});

Editor.displayName = 'Editor';

export default Editor; 