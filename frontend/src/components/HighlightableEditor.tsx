/**
 * HighlightableEditor Component - Clean Architecture Implementation
 * 
 * REFACTORED using Atomic Design principles:
 * - Single Responsibility: Coordinate highlighting workflow
 * - Delegates specific responsibilities to focused sub-components
 * - Uses composition over complex state management
 * - Follows React best practices for maintainability
 */

import React, { useCallback, useRef, useState } from 'react';
import { Editor } from '@tiptap/react';
import { useChatContext } from '../contexts/ChatContext';
import { useEditorContext } from '../contexts/EditorContext';
import {
  HighlightManager,
  EditorCoreWithRef,
  HighlightTooltip,
  HighlightsSidebar
} from './editor-features';
import '../styles/highlightable-editor.css';

interface HighlightableEditorProps {
  content?: string;
  onChange?: (content: string) => void;
  onTextHighlighted?: (text: string, highlightId: string) => void;
  onHighlightRemoved?: (highlightId: string) => void;
}

/**
 * Template Component: HighlightableEditor
 * 
 * CLEAN ARCHITECTURE IMPLEMENTATION:
 * - Single Responsibility: Coordinate editor and highlighting functionality
 * - Composition: Uses specialized components for each concern
 * - Separation of Concerns: UI logic separated from business logic
 * - Testability: Each sub-component can be tested independently
 */
const HighlightableEditor: React.FC<HighlightableEditorProps> = ({
  content,
  onChange,
  onTextHighlighted,
  onHighlightRemoved
}) => {
  // Context integration
  const { handleTextHighlighted } = useChatContext();
  const { 
    editorContent: contextContent, 
    setEditorContent: contextOnChange
  } = useEditorContext();

  // Use props if provided, otherwise use context
  const contentProp = content !== undefined ? content : contextContent;
  const onChangeProp = onChange || contextOnChange;
  const onTextHighlightedProp = onTextHighlighted || (() => {});
  const onHighlightRemovedProp = onHighlightRemoved || (() => {});

  // Local state for UI interactions
  const [showTooltip, setShowTooltip] = useState(false);
  const [tooltipPosition, setTooltipPosition] = useState({ x: 0, y: 0 });
  const [selectedText, setSelectedText] = useState('');
  
  // Ref to access editor instance
  const editorRef = useRef<{ editor: Editor | null } | null>(null);

  // Handle text selection from editor
  const handleSelectionChange = useCallback((text: string, position: { x: number; y: number }) => {
    if (text.trim() && text.length > 2) {
      setSelectedText(text);
      setTooltipPosition(position);
      setShowTooltip(true);
    } else {
      setShowTooltip(false);
      setSelectedText('');
    }
  }, []);

  // Handle highlight click
  const handleHighlightClick = useCallback((highlightId: string) => {
    console.log('Clicked highlight:', highlightId);
    // Could implement highlight editing or context menu here
  }, []);

  // Handle tooltip cancel
  const handleTooltipCancel = useCallback(() => {
    setShowTooltip(false);
    setSelectedText('');
  }, []);

  return (
    <div className="highlightable-editor-container">
      <HighlightManager>
        {({ highlights, createHighlight, removeHighlight }) => {
          // Handle creating highlight with chat integration
          const handleCreateHighlight = (color: string) => {
            if (!selectedText || !editorRef.current?.editor) return;

            const editor = editorRef.current.editor;
            const { from, to } = editor.state.selection;

            // Create highlight in editor
            const highlightId = createHighlight(selectedText, color, { from, to });
            
            // Apply highlight in TipTap editor
            editor.chain().focus().setHighlight({ 
              color, 
              id: highlightId 
            }).run();

            // Integrate with chat context
            handleTextHighlighted(selectedText);
            
            // Notify parent component
            onTextHighlightedProp(selectedText, highlightId);

            // Clear selection and hide tooltip
            setShowTooltip(false);
            setSelectedText('');
            editor.commands.setTextSelection(to);
          };

          // Handle removing highlight
          const handleRemoveHighlight = (highlightId: string) => {
            if (!editorRef.current?.editor) return;

            const editor = editorRef.current.editor;
            const highlight = highlights.find(h => h.id === highlightId);
            
            if (highlight) {
              // Remove from editor
              const { from, to } = highlight.position;
              editor.chain().focus().setTextSelection({ from, to }).unsetHighlight().run();
              
              // Remove from state
              removeHighlight(highlightId);
              
              // Notify parent
              onHighlightRemovedProp(highlightId);
            }
          };

          // Handle clearing all highlights
          const handleClearAllHighlights = () => {
            highlights.forEach(highlight => {
              handleRemoveHighlight(highlight.id);
            });
          };

          return (
            <>
              {/* Editor Core */}
              <EditorCoreWithRef
                ref={editorRef}
                content={contentProp}
                onChange={onChangeProp}
                onSelectionChange={handleSelectionChange}
                onHighlightClick={handleHighlightClick}
              />
              
              {/* Highlight Tooltip */}
              <HighlightTooltip
                isVisible={showTooltip}
                position={tooltipPosition}
                selectedText={selectedText}
                onCreateHighlight={handleCreateHighlight}
                onCancel={handleTooltipCancel}
              />
              
              {/* Highlights Sidebar */}
              <HighlightsSidebar
                highlights={highlights}
                onRemoveHighlight={handleRemoveHighlight}
                onClearAll={handleClearAllHighlights}
              />
            </>
          );
        }}
      </HighlightManager>
    </div>
  );
};

HighlightableEditor.displayName = 'HighlightableEditor';

export default HighlightableEditor; 