import React, { useCallback } from 'react';
import DocumentTitleBar from '../DocumentTitleBar';
import DocumentHelp from '../DocumentHelp';
import HighlightableEditor from '../HighlightableEditor';
import { TextSelectionHandler } from './TextSelectionHandler';
import { useEditorContext } from '../../contexts/EditorContext';
import { useAuth } from '../../contexts/AuthContext';
import '../../styles/editor-panel.css';

/**
 * EditorPanel - Focused editor layout component
 * 
 * RESPONSIBILITIES:
 * - Editor layout structure
 * - Coordinating editor sub-components
 * - Managing editor-specific UI elements
 * - Connecting editor changes to document management
 * 
 * DOES NOT:
 * - Manage chat state
 * - Handle global events
 * - Duplicate state from contexts
 */
export const EditorPanel: React.FC = () => {
  const { editorContent, setEditorContent, documentManager } = useEditorContext();
  const { isAuthenticated } = useAuth();

  // CRITICAL FIX: Connect editor content changes to document management
  // This matches the pattern used in WritingWorkspace.tsx
  const handleEditorContentChange = useCallback((content: string) => {
    setEditorContent(content); // Update local editor state
    if (isAuthenticated && documentManager.currentDocument) {
      documentManager.updateContent(content); // Update document management state
    }
  }, [isAuthenticated, documentManager, setEditorContent]);

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
          onChange={handleEditorContentChange}
        />
        
        {/* Text Selection Handler - Separate concern */}
        <TextSelectionHandler />
      </div>
    </div>
  );
};

export default EditorPanel;