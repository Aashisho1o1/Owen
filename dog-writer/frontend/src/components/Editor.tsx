import { useEditor, EditorContent } from '@tiptap/react';
import StarterKit from '@tiptap/starter-kit';
import Paragraph from '@tiptap/extension-paragraph';
import React, { useCallback, useEffect, useState } from 'react';

interface EditorProps {
  content: string;
  onChange: (content: string) => void;
  onTextHighlighted: (text: string) => void;
}

const Editor: React.FC<EditorProps> = ({ content, onChange, onTextHighlighted }) => {
  const [fontSize, setFontSize] = useState('16px');
  const [fontFamily, setFontFamily] = useState('Inter');
  
  const editor = useEditor({
    extensions: [
      StarterKit,
      Paragraph,
    ],
    content: '',
    onUpdate: ({ editor }) => {
      onChange(editor.getHTML());
    },
  });
  
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
    <div className="editor-container">
      <div className="editor-header">
        <h2>Text Content</h2>
        <p className="selection-hint">Highlight text to discuss with the AI</p>
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
          padding: 20px;
        }
        
        .ProseMirror {
          outline: none;
          min-height: 100%;
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
};

export default Editor; 