/**
 * HighlightableEditor Component - Clean Architecture Implementation
 * 
 * REFACTORED using Atomic Design principles:
 * - Single Responsibility: Coordinate highlighting workflow
 * - Delegates specific responsibilities to focused sub-components
 * - Uses composition over complex state management
 * - Follows React best practices for maintainability
 */

import React, { useEffect } from 'react';
import { useEditor, EditorContent } from '@tiptap/react';
import StarterKit from '@tiptap/starter-kit';
import { useEditorContext } from '../contexts/EditorContext';
import '../styles/highlightable-editor.css';

interface HighlightableEditorProps {
  content?: string;
  onChange?: (content: string) => void;
}

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

  // Use props if provided, otherwise use context
  const contentProp = content !== undefined ? content : contextContent;
  const onChangeProp = onChange || contextOnChange;

  const editor = useEditor({
    extensions: [
      StarterKit,
    ],
    content: contentProp || '',
    onUpdate: ({ editor }) => {
      const newContent = editor.getHTML();
      onChangeProp(newContent);
    },
  });

  // Handle active discussion highlighting from ChatContext using DOM manipulation
  useEffect(() => {
    const handleActiveDiscussionHighlight = (event: CustomEvent) => {
      if (!editor) return;

      const { text, action } = event.detail;
      const editorElement = editor.view.dom;
      
      if (action === 'add' && text) {
        // Remove existing highlights
        const existingHighlights = editorElement.querySelectorAll('.active-discussion-highlight');
        existingHighlights.forEach(el => {
          const parent = el.parentNode;
          if (parent) {
            parent.replaceChild(document.createTextNode(el.textContent || ''), el);
            parent.normalize();
          }
        });
        
        // Find and highlight the text using TreeWalker
        const walker = document.createTreeWalker(
          editorElement,
          NodeFilter.SHOW_TEXT,
          null
        );
        
        let textNode;
        while ((textNode = walker.nextNode())) {
          const nodeValue = textNode.nodeValue || '';
          const index = nodeValue.indexOf(text);
          
          if (index >= 0) {
            const range = document.createRange();
            range.setStart(textNode, index);
            range.setEnd(textNode, index + text.length);
            
            const span = document.createElement('span');
            span.className = 'active-discussion-highlight';
            span.style.cssText = `
              background: linear-gradient(135deg, rgba(255, 215, 0, 0.35) 0%, rgba(255, 193, 7, 0.3) 100%);
              color: #d84315 !important;
              border: 2px solid #ff9800;
              border-radius: 6px;
              padding: 2px 4px;
              font-weight: 700;
              text-decoration: underline;
              text-decoration-color: #ff9800;
              text-decoration-style: wavy;
              position: relative;
              animation: activeDiscussionPulse 2s ease-in-out infinite;
            `;
            
            try {
              range.surroundContents(span);
              
              // Add fire emoji indicator
              const emoji = document.createElement('span');
              emoji.textContent = '🔥';
              emoji.style.cssText = `
                position: absolute;
                top: -8px;
                right: -8px;
                font-size: 12px;
                z-index: 20;
                animation: bounce 1.5s ease-in-out infinite;
              `;
              span.appendChild(emoji);
              
              break; // Only highlight the first occurrence
            } catch (e) {
              console.log('Could not apply highlighting:', e);
            }
          }
        }
      } else if (action === 'remove') {
        // Remove all highlights
        const highlights = editorElement.querySelectorAll('.active-discussion-highlight');
        highlights.forEach(el => {
          const parent = el.parentNode;
          if (parent) {
            parent.replaceChild(document.createTextNode(el.textContent || ''), el);
            parent.normalize();
          }
        });
      }
    };

    window.addEventListener('applyActiveDiscussionHighlight', handleActiveDiscussionHighlight as EventListener);
    
    return () => {
      window.removeEventListener('applyActiveDiscussionHighlight', handleActiveDiscussionHighlight as EventListener);
    };
  }, [editor]);

  // Update editor content when the content prop changes
  useEffect(() => {
    if (editor && contentProp && editor.getHTML() !== contentProp) {
      editor.commands.setContent(contentProp);
    }
  }, [contentProp, editor]);

  return (
    <div className="highlightable-editor-container">
      <div className="editor-wrapper">
        <EditorContent 
          editor={editor} 
          className="highlightable-editor"
        />
      </div>
    </div>
  );
};

export default HighlightableEditor; 