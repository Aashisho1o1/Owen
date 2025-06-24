import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import HighlightableEditor from './HighlightableEditor';
import ChatPane from './ChatPane';
import { useDocuments } from '../hooks/useDocuments';
import { useAuth } from '../contexts/AuthContext';
import './WritingWorkspace.css';

/**
 * WritingWorkspace - Clean layout component with single responsibility
 * 
 * RESPONSIBILITIES:
 * - Layout structure for editor + chat panels
 * - Responsive design handling
 * - Chat toggle UI
 * 
 * DOES NOT:
 * - Manage state (delegates to contexts)
 * - Handle business logic (delegates to child components)
 * - Duplicate context state
 */
export const WritingWorkspace: React.FC = () => {
  const navigate = useNavigate();
  const { isAuthenticated } = useAuth();
  const {
    createDocument,
    updateContent,
    updateTitle,
    saveNow,
    isSaving,
    lastSaved,
    hasUnsavedChanges,
    currentDocument,
    setCurrentDocument
  } = useDocuments();

  const [editorContent, setEditorContent] = useState('');
  const [documentTitle, setDocumentTitle] = useState('Untitled Document');
  const [isInitialized, setIsInitialized] = useState(false);
  const [wordCount, setWordCount] = useState(0);

  // Auto-create a blank document when component mounts
  useEffect(() => {
    const initializeDocument = async () => {
      if (!isInitialized && isAuthenticated) {
        try {
          console.log('🚀 Creating new blank document...');
          const newDoc = await createDocument('Untitled Document');
          setCurrentDocument(newDoc);
          setEditorContent(newDoc.content || '');
          setDocumentTitle(newDoc.title);
          setIsInitialized(true);
          console.log('✅ Blank document created and ready');
        } catch (error) {
          console.error('❌ Failed to create blank document:', error);
          // Continue with local state even if document creation fails
          setIsInitialized(true);
        }
      } else if (!isAuthenticated) {
        // Allow writing without authentication, but no saving
        setIsInitialized(true);
      }
    };

    initializeDocument();
  }, [isAuthenticated, isInitialized, createDocument, setCurrentDocument]);

  // Update document content when editor content changes
  useEffect(() => {
    if (currentDocument && editorContent !== currentDocument.content) {
      updateContent(editorContent);
    }
    
    // Update word count
    const words = editorContent.trim().split(/\s+/).filter(word => word.length > 0);
    setWordCount(words.length);
  }, [editorContent, currentDocument, updateContent]);

  // Update document title when title changes
  useEffect(() => {
    if (currentDocument && documentTitle !== currentDocument.title) {
      updateTitle(documentTitle);
    }
  }, [documentTitle, currentDocument, updateTitle]);

  const handleSaveNow = async () => {
    if (!isAuthenticated) {
      // Prompt user to sign in
      alert('Please sign in to save your work');
      return;
    }
    
    try {
      await saveNow();
    } catch (err) {
      console.error('Failed to save document:', err);
    }
  };

  const handleGoToDocuments = () => {
    navigate('/documents');
  };

  const formatLastSaved = () => {
    if (!lastSaved) return 'Never saved';
    const now = new Date();
    const diffMs = now.getTime() - lastSaved.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    
    if (diffMins < 1) return 'Saved just now';
    if (diffMins === 1) return 'Saved 1 minute ago';
    if (diffMins < 60) return `Saved ${diffMins} minutes ago`;
    return `Saved at ${lastSaved.toLocaleTimeString()}`;
  };

  if (!isInitialized) {
    return (
      <div className="writing-workspace loading">
        <div className="loading-content">
          <div className="loading-spinner"></div>
          <p>Preparing your writing space...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="writing-workspace">
      {/* Minimal header - focused on writing */}
      <div className="workspace-header">
        <div className="header-left">
          <input
            type="text"
            value={documentTitle}
            onChange={(e) => setDocumentTitle(e.target.value)}
            className="document-title-input"
            placeholder="Give your document a title..."
          />
        </div>
        
        <div className="header-center">
          <div className="save-status">
            {!isAuthenticated ? (
              <span className="guest-mode">Guest Mode - Sign in to save</span>
            ) : isSaving ? (
              <span className="saving">Saving...</span>
            ) : hasUnsavedChanges ? (
              <span className="unsaved">Unsaved changes</span>
            ) : (
              <span className="saved">{formatLastSaved()}</span>
            )}
          </div>
        </div>

        <div className="header-right">
          <div className="document-stats">
            <span className="word-count">{wordCount} words</span>
          </div>
          {isAuthenticated && hasUnsavedChanges && (
            <button onClick={handleSaveNow} className="save-now-btn">
              Save Now
            </button>
          )}
          <button onClick={handleGoToDocuments} className="documents-btn">
            All Documents
          </button>
        </div>
      </div>

      {/* Main writing area with editor and chat side by side */}
      <div className="workspace-main">
        <div className="editor-section">
          <div className="editor-container">
            <HighlightableEditor
              content={editorContent}
              onChange={setEditorContent}
            />
          </div>
        </div>

        {/* Chat panel - always visible on the right */}
        <div className="chat-section">
          <ChatPane />
        </div>
      </div>
    </div>
  );
};

export default WritingWorkspace; 