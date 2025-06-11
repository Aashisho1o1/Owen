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
  
  // Grammar checking state
  const [grammarIssues, setGrammarIssues] = useState<GrammarIssue[]>([]);
  const [isCheckingGrammar, setIsCheckingGrammar] = useState(false);
  const [enableGrammarCheck, setEnableGrammarCheck] = useState(true);
  const [showGrammarPanel, setShowGrammarPanel] = useState(false);
  const [lastGrammarCheck, setLastGrammarCheck] = useState<GrammarCheckResult | null>(null);
  
  const editor = useEditor({
    extensions: [
      StarterKit,
      Paragraph,
    ],
    content: content || '',
    onUpdate: ({ editor }) => {
      const newContent = editor.getHTML();
      onChange(newContent);
      
      // Grammar checking on content change
      if (enableGrammarCheck) {
        handleGrammarCheck(editor.getText());
      }
    },
  });

  // Grammar checking function
  const handleGrammarCheck = useCallback((text: string) => {
    if (!text.trim() || text.length < 10) {
      setGrammarIssues([]);
      return;
    }
    
    setIsCheckingGrammar(true);
    
    grammarService.checkRealTimeDebounced(text, (result: GrammarCheckResult) => {
      setGrammarIssues(result.issues);
      setLastGrammarCheck(result);
      setIsCheckingGrammar(false);
    });
  }, []);

  // Comprehensive grammar check
  const handleComprehensiveCheck = useCallback(async () => {
    if (!editor) return;
    
    const text = editor.getText();
    if (!text.trim()) return;
    
    setIsCheckingGrammar(true);
    
    try {
      const result = await grammarService.checkComprehensive(text);
      setGrammarIssues(result.issues);
      setLastGrammarCheck(result);
    } catch (error) {
      console.error('Comprehensive grammar check failed:', error);
    } finally {
      setIsCheckingGrammar(false);
    }
  }, [editor]);

  // Apply grammar suggestion
  const applySuggestion = useCallback((issue: GrammarIssue, suggestion: string) => {
    if (!editor) return;
    
    const currentText = editor.getText();
    const beforeText = currentText.substring(0, issue.start);
    const afterText = currentText.substring(issue.end);
    const newText = beforeText + suggestion + afterText;
    
    editor.commands.setContent(newText);
    setGrammarIssues(prev => prev.filter(i => i !== issue));
  }, [editor]);

  // Dismiss grammar issue
  const dismissIssue = useCallback((issue: GrammarIssue) => {
    setGrammarIssues(prev => prev.filter(i => i !== issue));
  }, []);

  // Update editor content when the content prop changes
  useEffect(() => {
    if (editor && content && editor.getHTML() !== content) {
      editor.commands.setContent(content);
    }
  }, [content, editor]);
  
  // Set up placeholder effect
  useEffect(() => {
    if (editor && editor.isEmpty) {
      // Add placeholder class to the editor
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
        <p className="selection-hint">Highlight text to discuss with the AI</p>
        
        {/* Grammar Controls - Integrated into existing header */}
        <div className="grammar-controls">
          <div className="grammar-status">
            <span className={`status-indicator ${isCheckingGrammar ? 'checking' : 'idle'}`}>
              {isCheckingGrammar ? '🔍 Checking...' : '✓ Grammar'}
            </span>
            <span className="issue-count">
              {grammarIssues.length} issues
            </span>
          </div>
          
          <div className="grammar-actions">
            <label className="toggle-grammar">
              <input
                type="checkbox"
                checked={enableGrammarCheck}
                onChange={(e) => setEnableGrammarCheck(e.target.checked)}
              />
              Real-time grammar
            </label>
            
            <button 
              onClick={handleComprehensiveCheck}
              disabled={isCheckingGrammar}
              className="comprehensive-check-btn"
            >
              Deep Check
            </button>
            
            {grammarIssues.length > 0 && (
              <button
                onClick={() => setShowGrammarPanel(!showGrammarPanel)}
                className="toggle-issues-btn"
              >
                {showGrammarPanel ? 'Hide' : 'Show'} Issues
              </button>
            )}
          </div>
        </div>
        
        <div className="format-controls">
          <div className="font-controls">
            <select 
              className="font-family-select" 
              value={fontFamily}
              onChange={(e) => setFontFamily(e.target.value)}
            >
              <option value="Inter">Inter</option>
              <option value="Arial">Arial</option>
              <option value="Times New Roman">Times New Roman</option>
              <option value="Georgia">Georgia</option>
              <option value="Courier New">Courier New</option>
            </select>
            
            <select 
              className="font-size-select" 
              value={fontSize}
              onChange={(e) => setFontSize(e.target.value)}
            >
              <option value="12px">12px</option>
              <option value="14px">14px</option>
              <option value="16px">16px</option>
              <option value="18px">18px</option>
              <option value="20px">20px</option>
              <option value="24px">24px</option>
            </select>
          </div>
          
          <div className="editor-tools">
            <button 
              className="tool-button" 
              onClick={() => editor?.chain().focus().toggleBold().run()}
              data-active={editor?.isActive('bold')}
            >
              <strong>B</strong>
            </button>
            <button 
              className="tool-button" 
              onClick={() => editor?.chain().focus().toggleItalic().run()}
              data-active={editor?.isActive('italic')}
            >
              <em>I</em>
            </button>
            <button 
              className="tool-button" 
              onClick={() => editor?.chain().focus().toggleHeading({ level: 2 }).run()}
              data-active={editor?.isActive('heading', { level: 2 })}
            >
              Heading
            </button>
            <button 
              className="tool-button" 
              onClick={() => editor?.chain().focus().toggleBulletList().run()}
              data-active={editor?.isActive('bulletList')}
            >
              Bullet
            </button>
          </div>
        </div>
      </div>
      
      <div className="editor-content">
        <EditorContent editor={editor} />
        
        {/* Grammar Issues Panel - Slides down when toggled */}
        {showGrammarPanel && grammarIssues.length > 0 && (
          <div className="grammar-issues-panel">
            <div className="issues-header">
              <h4>Grammar Issues ({grammarIssues.length})</h4>
              <button 
                onClick={() => setGrammarIssues([])}
                className="clear-issues-btn"
              >
                Clear All
              </button>
            </div>
            
            <div className="issues-list">
              {grammarIssues.map((issue, index) => (
                <div key={index} className={`issue-item severity-${issue.severity}`}>
                  <div className="issue-header">
                    <span className="issue-type">{issue.issue_type}</span>
                    <span className="issue-source">{issue.source}</span>
                  </div>
                  
                  <div className="issue-message">{issue.message}</div>
                  
                  {issue.suggestions.length > 0 && (
                    <div className="issue-suggestions">
                      {issue.suggestions.slice(0, 3).map((suggestion, i) => (
                        <button
                          key={i}
                          onClick={() => applySuggestion(issue, suggestion)}
                          className="suggestion-btn"
                        >
                          {suggestion}
                        </button>
                      ))}
                    </div>
                  )}
                  
                  <button 
                    onClick={() => dismissIssue(issue)}
                    className="dismiss-btn"
                  >
                    Dismiss
                  </button>
                </div>
              ))}
            </div>
          </div>
        )}
        
        {/* Footer with check info */}
        {lastGrammarCheck && (
          <div className="editor-footer">
            <span className="check-info">
              Last check: {lastGrammarCheck.processing_time_ms}ms
              {lastGrammarCheck.cached && ' (cached)'}
            </span>
            <span className="word-count">
              {lastGrammarCheck.word_count} words
            </span>
          </div>
        )}
      </div>
      <style>{`
        .editor-container {
          display: flex;
          flex-direction: column;
          height: 100%;
          border-radius: var(--rounded-xl);
          overflow: hidden;
          background-color: white;
        }
        
        .editor-header {
          padding: 12px 16px;
          border-bottom: 1px solid #e2e8f0;
          background-color: white;
          display: flex;
          flex-direction: column;
          align-items: flex-start;
          gap: 12px;
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
        
        /* Grammar Controls */
        .grammar-controls {
          display: flex;
          justify-content: space-between;
          align-items: center;
          width: 100%;
          padding: 8px 12px;
          background: #f8fafc;
          border-radius: 6px;
          border: 1px solid #e2e8f0;
        }
        
        .grammar-status {
          display: flex;
          align-items: center;
          gap: 12px;
        }
        
        .status-indicator {
          font-size: 14px;
          color: #374151;
        }
        
        .status-indicator.checking {
          color: #3b82f6;
        }
        
        .issue-count {
          font-size: 12px;
          color: #6b7280;
          background: #e5e7eb;
          padding: 2px 6px;
          border-radius: 3px;
        }
        
        .grammar-actions {
          display: flex;
          align-items: center;
          gap: 12px;
        }
        
        .toggle-grammar {
          display: flex;
          align-items: center;
          gap: 6px;
          font-size: 12px;
          cursor: pointer;
          color: #374151;
        }
        
        .comprehensive-check-btn, .toggle-issues-btn {
          padding: 4px 8px;
          background: #3b82f6;
          color: white;
          border: none;
          border-radius: 4px;
          cursor: pointer;
          font-size: 12px;
          transition: background 0.2s;
        }
        
        .comprehensive-check-btn:hover, .toggle-issues-btn:hover {
          background: #2563eb;
        }
        
        .comprehensive-check-btn:disabled {
          opacity: 0.5;
          cursor: not-allowed;
        }
        
        .toggle-issues-btn {
          background: #6b7280;
        }
        
        .toggle-issues-btn:hover {
          background: #4b5563;
        }
        
        /* Grammar Issues Panel */
        .grammar-issues-panel {
          background: #fafafa;
          border-top: 1px solid #e2e8f0;
          padding: 12px;
          max-height: 300px;
          overflow-y: auto;
        }
        
        .issues-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 12px;
        }
        
        .issues-header h4 {
          margin: 0;
          font-size: 14px;
          color: #374151;
        }
        
        .clear-issues-btn {
          padding: 4px 8px;
          background: #ef4444;
          color: white;
          border: none;
          border-radius: 4px;
          cursor: pointer;
          font-size: 11px;
        }
        
        .issues-list {
          display: flex;
          flex-direction: column;
          gap: 8px;
        }
        
        .issue-item {
          background: white;
          border: 1px solid #e2e8f0;
          border-radius: 6px;
          padding: 10px;
        }
        
        .issue-item.severity-error {
          border-left: 4px solid #ef4444;
        }
        
        .issue-item.severity-warning {
          border-left: 4px solid #f59e0b;
        }
        
        .issue-item.severity-info {
          border-left: 4px solid #3b82f6;
        }
        
        .issue-item .issue-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 6px;
        }
        
        .issue-type {
          background: #e5e7eb;
          color: #374151;
          padding: 2px 6px;
          border-radius: 3px;
          font-size: 10px;
          font-weight: 500;
          text-transform: uppercase;
        }
        
        .issue-source {
          font-size: 10px;
          color: #6b7280;
        }
        
        .issue-message {
          font-size: 13px;
          color: #374151;
          margin-bottom: 8px;
          line-height: 1.4;
        }
        
        .issue-suggestions {
          display: flex;
          flex-wrap: wrap;
          gap: 4px;
          margin-bottom: 8px;
        }
        
        .suggestion-btn {
          padding: 3px 6px;
          background: #e0f2fe;
          color: #0284c7;
          border: 1px solid #bae6fd;
          border-radius: 3px;
          cursor: pointer;
          font-size: 11px;
          transition: all 0.2s;
        }
        
        .suggestion-btn:hover {
          background: #0284c7;
          color: white;
        }
        
        .dismiss-btn {
          padding: 3px 6px;
          background: transparent;
          color: #6b7280;
          border: 1px solid #d1d5db;
          border-radius: 3px;
          cursor: pointer;
          font-size: 11px;
          transition: all 0.2s;
        }
        
        .dismiss-btn:hover {
          background: #f3f4f6;
          color: #374151;
        }
        
        /* Editor Footer */
        .editor-footer {
          display: flex;
          justify-content: space-between;
          padding: 8px 12px;
          background: #f9fafb;
          border-top: 1px solid #e5e7eb;
          font-size: 11px;
          color: #6b7280;
        }
        
        .format-controls {
          display: flex;
          justify-content: space-between;
          align-items: center;
          width: 100%;
          flex-wrap: wrap;
          gap: 12px;
        }
        
        .font-controls {
          display: flex;
          gap: 8px;
        }
        
        .font-family-select, .font-size-select {
          padding: 6px 8px;
          border: 1px solid #e2e8f0;
          border-radius: var(--rounded-md);
          background-color: white;
          font-size: 0.875rem;
          color: var(--text-primary);
          outline: none;
        }
        
        .font-family-select {
          min-width: 140px;
        }
        
        .font-size-select {
          min-width: 70px;
        }
        
        .editor-tools {
          display: flex;
          gap: 8px;
        }
        
        .tool-button {
          min-width: 36px;
          height: 36px;
          border-radius: var(--rounded-md);
          border: 1px solid #e2e8f0;
          background-color: white;
          display: flex;
          align-items: center;
          justify-content: center;
          cursor: pointer;
          transition: all 0.2s;
          color: var(--text-primary);
          font-size: 0.875rem;
          padding: 0 8px;
        }
        
        .tool-button:hover {
          background-color: #f8fafc;
          color: var(--text-primary);
          border-color: #cbd5e1;
        }
        
        .tool-button[data-active="true"] {
          background-color: var(--primary-color);
          color: white;
          border-color: var(--primary-color);
        }
        
        .editor-content {
          flex: 1;
          overflow-y: auto;
          display: flex;
          flex-direction: column;
        }
        
        .ProseMirror {
          outline: none;
          flex: 1;
          padding: 20px;
          line-height: 1.6;
          color: var(--text-primary);
        }
        
        .ProseMirror.is-empty:before {
          content: 'Start writing your masterpiece here...';
          color: var(--text-secondary);
          opacity: 0.6;
          font-style: italic;
          position: absolute;
          pointer-events: none;
        }
        
        .ProseMirror p {
          margin-bottom: 1em;
        }
        
        .ProseMirror h1,
        .ProseMirror h2,
        .ProseMirror h3 {
          margin-top: 1.5em;
          margin-bottom: 0.75em;
          font-weight: 600;
        }
        
        .ProseMirror h1 {
          font-size: 1.875rem;
        }
        
        .ProseMirror h2 {
          font-size: 1.5rem;
        }
        
        .ProseMirror h3 {
          font-size: 1.25rem;
        }
        
        .ProseMirror ul,
        .ProseMirror ol {
          padding-left: 1.5em;
          margin-bottom: 1em;
        }
        
        .ProseMirror li {
          margin-bottom: 0.5em;
        }
        
        .ProseMirror blockquote {
          border-left: 3px solid var(--primary-light);
          padding-left: 1em;
          margin-left: 0;
          color: var(--text-secondary);
        }
        
        /* Highlight selected text */
        .ProseMirror ::selection {
          background-color: var(--primary-light);
          color: white;
        }
      `}</style>
    </div>
  );
});

Editor.displayName = 'Editor';

export default Editor; 