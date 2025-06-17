import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useDocuments } from '../hooks/useDocuments';
import { useDocumentTheme } from '../contexts/DocumentThemeContext';
import HighlightableEditor from '../components/HighlightableEditor';
import ChatPane from '../components/ChatPane';
import './DocumentEditor.css';

const DocumentEditor: React.FC = () => {
  const { documentId } = useParams<{ documentId: string }>();
  const navigate = useNavigate();
  const { 
    currentDocument, 
    setCurrentDocument, 
    getDocument, 
    updateContent, 
    updateTitle,
    saveNow,
    isSaving,
    lastSaved,
    hasUnsavedChanges 
  } = useDocuments();
  
  const { applyDocumentTheme, clearDocumentTheme, isDocumentThemeActive } = useDocumentTheme();
  
  const [isChatOpen, setIsChatOpen] = useState(false);
  const [editorContent, setEditorContent] = useState('');
  const [documentTitle, setDocumentTitle] = useState('');
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Load document on mount
  useEffect(() => {
    const loadDocument = async () => {
      if (!documentId) {
        setError('No document ID provided');
        setIsLoading(false);
        return;
      }

      try {
        setIsLoading(true);
        const doc = await getDocument(documentId);
        setCurrentDocument(doc);
        setEditorContent(doc.content);
        setDocumentTitle(doc.title);
        
        // Apply document theme if available in tags
        const themeTag = doc.tags?.find(tag => tag.startsWith('theme:'));
        if (themeTag) {
          const themeId = themeTag.replace('theme:', '');
          applyDocumentTheme(themeId);
        } else {
          clearDocumentTheme();
        }
        
        setError(null);
      } catch (err) {
        console.error('Failed to load document:', err);
        setError('Failed to load document');
      } finally {
        setIsLoading(false);
      }
    };

    loadDocument();
    
    // Cleanup theme when component unmounts or document changes
    return () => {
      clearDocumentTheme();
    };
  }, [documentId, getDocument, setCurrentDocument, applyDocumentTheme, clearDocumentTheme]);

  // Update document content when editor changes
  useEffect(() => {
    if (currentDocument && editorContent !== currentDocument.content) {
      updateContent(editorContent);
    }
  }, [editorContent, currentDocument, updateContent]);

  // Update document title when title changes
  useEffect(() => {
    if (currentDocument && documentTitle !== currentDocument.title) {
      updateTitle(documentTitle);
    }
  }, [documentTitle, currentDocument, updateTitle]);

  const toggleChat = () => {
    setIsChatOpen(!isChatOpen);
  };

  const handleSaveNow = async () => {
    try {
      await saveNow();
    } catch (err) {
      console.error('Failed to save document:', err);
    }
  };

  const handleBackToDocuments = () => {
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

  if (isLoading) {
    return (
      <div className="document-editor loading">
        <div className="loading-content">
          <div className="loading-spinner"></div>
          <p>Loading document...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="document-editor error">
        <div className="error-content">
          <h2>Error Loading Document</h2>
          <p>{error}</p>
          <button onClick={handleBackToDocuments} className="back-button">
            Back to Documents
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className={`document-editor ${isDocumentThemeActive ? 'themed document-themed' : ''}`}>
      {/* Header with document controls */}
      <div className="editor-header">
        <div className="header-left">
          <button onClick={handleBackToDocuments} className="back-button">
            ← Back to Documents
          </button>
          <div className="document-info">
            <input
              type="text"
              value={documentTitle}
              onChange={(e) => setDocumentTitle(e.target.value)}
              className="document-title-input"
              placeholder="Document title..."
            />
            <div className="save-status">
              {isSaving ? (
                <span className="saving">Saving...</span>
              ) : hasUnsavedChanges ? (
                <span className="unsaved">Unsaved changes</span>
              ) : (
                <span className="saved">{formatLastSaved()}</span>
              )}
              {hasUnsavedChanges && (
                <button onClick={handleSaveNow} className="save-now-btn">
                  Save Now
                </button>
              )}
            </div>
          </div>
        </div>
        
        <div className="header-right">
          <div className="word-count">
            {currentDocument?.word_count || 0} words
          </div>
          <button 
            className={`chat-toggle ${isChatOpen ? 'active' : ''}`}
            onClick={toggleChat}
          >
            {isChatOpen ? 'Close Chat' : 'AI Chat'}
          </button>
        </div>
      </div>

      {/* Main editor area */}
      <div className={`editor-main ${isChatOpen ? 'with-chat' : 'full-width'}`}>
        <div className={`editor-container ${isDocumentThemeActive ? 'themed' : ''}`}>
          <HighlightableEditor
            content={editorContent}
            onChange={setEditorContent}
            onTextHighlighted={() => {}}
          />
        </div>

        {/* Chat panel */}
        {isChatOpen && (
          <div className="chat-container">
            <ChatPane />
          </div>
        )}
      </div>
    </div>
  );
};

export default DocumentEditor; 