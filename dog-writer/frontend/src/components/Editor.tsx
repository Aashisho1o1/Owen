import { useEditor, EditorContent } from '@tiptap/react';
import StarterKit from '@tiptap/starter-kit';
import Paragraph from '@tiptap/extension-paragraph';
import React, { useCallback, useEffect, useState, forwardRef } from 'react';
import { useAppContext } from '../contexts/AppContext';

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
  
  const editor = useEditor({
    extensions: [
      StarterKit,
      Paragraph,
    ],
    content: content || '',
    onUpdate: ({ editor }) => {
      const newContent = editor.getHTML();
      onChange(newContent);
    },
  });

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
      </div>
      
      <div className="editor-content">
        <EditorContent editor={editor} />
      </div>

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
      `}</style>
    </div>
  );
});

Editor.displayName = 'Editor';

export default Editor; 