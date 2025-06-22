import React, { useCallback, useEffect, useState } from 'react';
import { useEditor, EditorContent } from '@tiptap/react';
import StarterKit from '@tiptap/starter-kit';
import { CustomHighlight, HighlightInfo } from './CustomHighlightExtension';

interface EditorCoreProps {
  content: string;
  onChange: (content: string) => void;
  onSelectionChange: (selectedText: string, position: { x: number; y: number }) => void;
  onHighlightClick: (highlightId: string) => void;
}

/**
 * Organism Component: Editor Core
 * Single Responsibility: Manage the TipTap editor instance and core functionality
 */
export const EditorCore: React.FC<EditorCoreProps> = ({
  content,
  onChange,
  onSelectionChange,
  onHighlightClick
}) => {
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
        // Get the position of the selection for tooltip placement
        const coords = editor.view.coordsAtPos(from);
        onSelectionChange(selectedText.trim(), {
          x: coords.left,
          y: coords.top - 60, // Position above the selection
        });
      } else {
        onSelectionChange('', { x: 0, y: 0 });
      }
    },
  });

  // Handle clicking on existing highlights
  useEffect(() => {
    if (!editor) return;

    const handleClick = (event: MouseEvent) => {
      const target = event.target as HTMLElement;
      const highlightElement = target.closest('[data-highlight-id]');
      
      if (highlightElement) {
        const highlightId = highlightElement.getAttribute('data-highlight-id');
        if (highlightId) {
          onHighlightClick(highlightId);
        }
      }
    };

    const editorElement = editor.view.dom;
    editorElement.addEventListener('click', handleClick);

    return () => {
      editorElement.removeEventListener('click', handleClick);
    };
  }, [editor, onHighlightClick]);

  // Update editor content when the content prop changes
  useEffect(() => {
    if (editor && content && editor.getHTML() !== content) {
      editor.commands.setContent(content);
    }
  }, [content, editor]);

  // Expose editor instance for parent components
  React.useImperativeHandle(React.forwardRef(() => null), () => ({
    editor
  }), [editor]);

  return (
    <div className="editor-wrapper">
      <EditorContent 
        editor={editor} 
        className="highlightable-editor"
      />
    </div>
  );
};

// Forward ref version for accessing editor instance
export const EditorCoreWithRef = React.forwardRef<{ editor: any }, EditorCoreProps>((props, ref) => {
  const editor = useEditor({
    extensions: [
      StarterKit,
      CustomHighlight.configure({
        multicolor: true,
      }),
    ],
    content: props.content || '',
    onUpdate: ({ editor }) => {
      const newContent = editor.getHTML();
      props.onChange(newContent);
    },
    onSelectionUpdate: ({ editor }) => {
      const { from, to } = editor.state.selection;
      const selectedText = editor.state.doc.textBetween(from, to, ' ');
      
      if (selectedText.trim() && selectedText.length > 2) {
        const coords = editor.view.coordsAtPos(from);
        props.onSelectionChange(selectedText.trim(), {
          x: coords.left,
          y: coords.top - 60,
        });
      } else {
        props.onSelectionChange('', { x: 0, y: 0 });
      }
    },
  });

  React.useImperativeHandle(ref, () => ({
    editor
  }), [editor]);

  return (
    <div className="editor-wrapper">
      <EditorContent 
        editor={editor} 
        className="highlightable-editor"
      />
    </div>
  );
});

EditorCoreWithRef.displayName = 'EditorCoreWithRef';
