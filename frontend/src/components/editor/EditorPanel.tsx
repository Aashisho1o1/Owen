import React from 'react';
import DocumentTitleBar from '../DocumentTitleBar';
import DocumentHelp from '../DocumentHelp';
import HighlightableEditor from '../HighlightableEditor';
import { TextSelectionHandler } from './TextSelectionHandler';
import { useEditorContext } from '../../contexts/EditorContext';
import '../../styles/editor-panel.css';

/**
 * EditorPanel - Focused editor layout component
 * 
 * RESPONSIBILITIES:
 * - Editor layout structure
 * - Coordinating editor sub-components
 * - Managing editor-specific UI elements
 * 
 * DOES NOT:
 * - Manage chat state
 * - Handle global events
 * - Duplicate state from contexts
 */
export const EditorPanel: React.FC = () => {
  const { editorContent, setEditorContent } = useEditorContext();

  return (
    <div className="editor-panel">
      {/* Document Title Bar */}
      <DocumentTitleBar />
      
      {/* Document Help Banner */}
      <DocumentHelp />
      
      {/* Editor Container with Text Selection */}
      <div className="editor-container">
        <HighlightableEditor
          content={editorContent}
          onChange={setEditorContent}
        />
        
        {/* Text Selection Handler - Separate concern */}
        <TextSelectionHandler />
      </div>
    </div>
  );
};

export default EditorPanel; 