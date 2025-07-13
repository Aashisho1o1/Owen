import React, { useState, useEffect } from 'react';
import HighlightableEditor from './HighlightableEditor';
import ChatPane from './ChatPane';
import { FictionDocumentManager } from './FictionDocumentManager';
import { useDocuments } from '../hooks/useDocuments';
import { useAuth } from '../contexts/AuthContext';
import { useChatContext } from '../contexts/ChatContext';
import { useEditorContext } from '../contexts/EditorContext';
import AuthModal from './AuthModal';
import UserProfileModal from './UserProfileModal';
import './WritingWorkspace.css';
import '../styles/FictionDocumentManager.css';

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
  const { isAuthenticated } = useAuth();
  const { isChatVisible, toggleChat } = useChatContext();
  const { editorContent, setEditorContent, documentManager } = useEditorContext();
  const {
    createDocument,
    updateTitle,
    saveNow,
    isSaving,
    lastSaved,
    hasUnsavedChanges,
    currentDocument,
    setCurrentDocument
  } = useDocuments();

  // Auth state for header
  const { user } = useAuth();
  const [showAuthModal, setShowAuthModal] = useState(false);
  const [showProfileModal, setShowProfileModal] = useState(false);

  const [documentTitle, setDocumentTitle] = useState('Untitled Document');
  const [isLoading, setIsLoading] = useState(true);
  const [isInitialized, setIsInitialized] = useState(false);
  
  // Copy functionality state
  const [copyStatus, setCopyStatus] = useState<'idle' | 'copying' | 'success' | 'error'>('idle');
  
  // Fiction Document Manager state
  const [showDocumentManager, setShowDocumentManager] = useState(false);

  // Initialize document on component mount
  useEffect(() => {
    const initializeDocument = async () => {
      try {
        setIsLoading(true);
        
        if (isAuthenticated) {
          // Create a new document for authenticated users
          const newDoc = await createDocument('Untitled Document');
          setCurrentDocument(newDoc);
          setDocumentTitle(newDoc.title);
          setEditorContent(newDoc.content || '');
        } else {
          // Guest mode - just set up local state
          setDocumentTitle('Untitled Document');
          setEditorContent('');
        }
        
        setIsInitialized(true);
      } catch (error) {
        console.error('Error initializing document:', error);
        // Fallback to guest mode
        setDocumentTitle('Untitled Document');
        setEditorContent('');
        setIsInitialized(true);
      } finally {
        setIsLoading(false);
      }
    };

    if (!isInitialized) {
      initializeDocument();
    }
  }, [isAuthenticated, isInitialized, createDocument, setCurrentDocument, setEditorContent]);

  // Handle title changes  
  const handleTitleChange = (title: string) => {
    setDocumentTitle(title);
    if (isAuthenticated && currentDocument) {
      updateTitle(title);
    }
  };

  // Manual save function
  const handleSaveNow = async () => {
    if (isAuthenticated && currentDocument) {
      try {
        await saveNow();
      } catch (error) {
        console.error('Error saving document:', error);
      }
    }
  };

  // Format last saved time
  const formatLastSaved = () => {
    if (!lastSaved) return '';
    const now = new Date();
    const diff = now.getTime() - lastSaved.getTime();
    const minutes = Math.floor(diff / 60000);
    
    if (minutes < 1) return 'Just now';
    if (minutes === 1) return '1 minute ago';
    if (minutes < 60) return `${minutes} minutes ago`;
    
    const hours = Math.floor(minutes / 60);
    if (hours === 1) return '1 hour ago';
    if (hours < 24) return `${hours} hours ago`;
    
    return lastSaved.toLocaleDateString();
  };

  // Handle document selection from Fiction Document Manager
  const handleDocumentSelect = (document: { id: string; title: string; content: string }) => {
    // Update the document manager with proper Document structure
    const fullDocument = {
      ...document,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
      user_id: 'current-user', // Will be properly set by the backend
      word_count: document.content.length,
      document_type: 'novel' as const
    };
    
    documentManager.setCurrentDocument(fullDocument);
    setEditorContent(document.content);
    setDocumentTitle(document.title);
    setShowDocumentManager(false);
  };

  // Copy document content to clipboard
  const handleCopyContent = async () => {
    try {
      setCopyStatus('copying');
      
      // Get plain text content (strip HTML tags if present)
      // Simple HTML stripping without external library
      const div = document.createElement('div');
      div.innerHTML = editorContent;
      const textContent = (div.textContent || div.innerText || '').trim();
      
      if (!textContent) {
        setCopyStatus('error');
        // Show a brief message for empty content
        console.log('No content to copy');
        setTimeout(() => setCopyStatus('idle'), 2000);
        return;
      }

      // Use modern clipboard API with fallback
      if (navigator.clipboard && window.isSecureContext) {
        await navigator.clipboard.writeText(textContent);
      } else {
        // Fallback for older browsers
        const textArea = document.createElement('textarea');
        textArea.value = textContent;
        textArea.style.position = 'fixed';
        textArea.style.left = '-999999px';
        textArea.style.top = '-999999px';
        document.body.appendChild(textArea);
        textArea.focus();
        textArea.select();
        document.execCommand('copy');
        textArea.remove();
      }
      
      setCopyStatus('success');
      setTimeout(() => setCopyStatus('idle'), 2000);
    } catch (error) {
      console.error('Failed to copy content:', error);
      setCopyStatus('error');
      setTimeout(() => setCopyStatus('idle'), 2000);
    }
  };

  // Remove auto-hide functionality for AI hint - keep it permanent
  // No useEffect needed for hiding the hint

  const handleAppMapClick = () => {
    // Owen Writer User Guide - App Map
    window.open('https://drive.google.com/file/d/1ab8nrRNUbZNAYsMThGVp9we3CapHMjfB/view?usp=sharing', '_blank');
  };

  if (isLoading) {
    return (
      <div className="writing-workspace loading">
        <div className="loading-content">
          <div className="loading-spinner"></div>
          <p>Setting up your writing space...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="writing-workspace">
      {/* Simplified Header - MVP Version */}
      <div className="workspace-header">
        {/* Header Controls Container - Side by side buttons - NOW ON THE LEFT */}
        <div className="header-buttons-container">
          {/* App Map Button - Using existing nav-action-button pattern */}
          <button
            className="nav-action-button"
            onClick={handleAppMapClick}
            type="button"
            aria-label="Open app navigation guide"
            title="App Map - Navigation Guide"
          >
            <span className="nav-action-icon" aria-hidden="true">🗺️</span>
            <span className="nav-action-text">App Map</span>
          </button>

          {/* Auth Button - Sign In or Profile */}
          {isAuthenticated && user ? (
            <button
              onClick={() => setShowProfileModal(true)}
              className="nav-action-button"
              type="button"
              aria-label="User profile"
              title="User Profile"
            >
              <div className="profile-avatar">
                {user.display_name?.charAt(0)?.toUpperCase() || user.email?.charAt(0)?.toUpperCase() || 'U'}
              </div>
              <span className="nav-action-text">Profile</span>
            </button>
          ) : (
            <button
              onClick={() => setShowAuthModal(true)}
              className="nav-action-button primary"
              type="button"
              aria-label="Sign in"
              title="Sign In"
            >
              <span className="nav-action-icon" aria-hidden="true">👤</span>
              <span className="nav-action-text">Sign In</span>
            </button>
          )}
        </div>
        
        {/* Document Title - NOW IN THE CENTER */}
        <div className="title-section">
          <input
            type="text"
            value={documentTitle}
            onChange={(e) => handleTitleChange(e.target.value)}
            className="document-title-input"
            placeholder="Untitled Document"
          />
        </div>
        
        {/* MVP Controls - Just essentials */}
        <div className="workspace-controls">
          {/* Document Manager Button */}
          <button
            onClick={() => setShowDocumentManager(true)}
            className="document-manager-btn"
            title="Open Fiction Document Manager"
          >
            <span className="manager-icon">📚</span>
            <span className="manager-text">Documents</span>
          </button>

          {/* Copy Button */}
          <button
            onClick={handleCopyContent}
            className={`copy-content-btn ${copyStatus}`}
            title="Copy document content to clipboard"
            disabled={copyStatus === 'copying' || !editorContent.trim()}
            aria-label={`Copy document content to clipboard. ${
              copyStatus === 'success' ? 'Content copied successfully!' :
              copyStatus === 'error' ? 'Failed to copy content' :
              copyStatus === 'copying' ? 'Copying content...' :
              !editorContent.trim() ? 'No content to copy' :
              'Copy document content'
            }`}
          >
            <span className="copy-icon" aria-hidden="true">
              {copyStatus === 'copying' && '⏳'}
              {copyStatus === 'success' && '✅'}
              {copyStatus === 'error' && '❌'}
              {copyStatus === 'idle' && '📋'}
            </span>
            <span className="copy-text">
              {copyStatus === 'copying' && 'Copying...'}
              {copyStatus === 'success' && 'Copied!'}
              {copyStatus === 'error' && 'Failed'}
              {copyStatus === 'idle' && 'Copy'}
            </span>
          </button>

          {/* Chat Toggle Button */}
          <button
            onClick={toggleChat}
            className={`chat-toggle-btn ${isChatVisible ? 'active' : ''}`}
            title={isChatVisible ? 'Hide AI Assistant' : 'Show AI Assistant'}
          >
            <span className="toggle-icon">
              {isChatVisible ? '💬' : '🤖'}
            </span>
            <span className="toggle-text">
              {isChatVisible ? 'Hide AI' : 'Show AI'}
            </span>
          </button>

          {/* Save Status - Only for authenticated users */}
          {isAuthenticated && (
            <div className="save-status">
              {isSaving && <span className="status-saving">Saving...</span>}
              {!isSaving && hasUnsavedChanges && (
                <button onClick={handleSaveNow} className="save-now-btn">
                  Save Now
                </button>
              )}
              {!isSaving && !hasUnsavedChanges && lastSaved && (
                <span className="status-saved">Saved {formatLastSaved()}</span>
              )}
            </div>
          )}
        </div>
      </div>

      {/* Main Workspace - Full height utilization */}
      <div className={`workspace-content ${isChatVisible ? 'with-chat' : 'editor-only'}`}>
        {/* Writing Area */}
        <div className="editor-section">
          <div className="editor-container">
            <HighlightableEditor
              content={documentManager.pendingContent}
              onChange={setEditorContent}
            />
            
            {/* Permanent AI Discovery Hint - Always visible */}
            <div className="ai-discovery-hint-permanent">
              <em>Highlight any text to unlock AI assistance</em>
            </div>
          </div>
        </div>

        {/* AI Chat Panel */}
        {isChatVisible && (
          <div className="chat-section">
            <ChatPane />
          </div>
        )}
      </div>

      {/* Fiction Document Manager Modal */}
      {showDocumentManager && (
        <FictionDocumentManager
          onDocumentSelect={handleDocumentSelect}
          onClose={() => setShowDocumentManager(false)}
        />
      )}

      {/* Auth Modals */}
      {showAuthModal && (
        <AuthModal
          isOpen={showAuthModal}
          onClose={() => setShowAuthModal(false)}
          initialMode="signin"
        />
      )}
      
      {showProfileModal && (
        <UserProfileModal
          isOpen={showProfileModal}
          onClose={() => setShowProfileModal(false)}
        />
      )}
    </div>
  );
};

export default WritingWorkspace; 