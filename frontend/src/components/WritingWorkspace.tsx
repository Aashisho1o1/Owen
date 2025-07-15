import React, { useState, useEffect } from 'react';
import HighlightableEditor from './HighlightableEditor';
import ChatPane from './ChatPane';
// FictionDocumentManager removed - template system deprecated
import { StoryGeneratorModal } from './StoryGeneratorModal';
import { useDocuments } from '../hooks/useDocuments';
import { useAuth } from '../contexts/AuthContext';
import { useChatContext } from '../contexts/ChatContext';
import { useEditorContext } from '../contexts/EditorContext';
import AuthModal from './AuthModal';
import UserProfileModal from './UserProfileModal';
import './WritingWorkspace.css';
// FictionDocumentManager.css removed - template system deprecated

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

  const [documentTitle, setDocumentTitle] = useState('untitled doc');
  const [isLoading, setIsLoading] = useState(true);
  const [isInitialized, setIsInitialized] = useState(false);
  
  // Copy functionality state

  
  // Fiction Document Manager state
  // showDocumentManager removed - template system deprecated
  
  // Story Generator state
  const [showStoryGenerator, setShowStoryGenerator] = useState(false);

  // Initialize document on component mount
  useEffect(() => {
    const initializeDocument = async () => {
      try {
        setIsLoading(true);
        
        if (isAuthenticated) {
          // Create a new document for authenticated users
          const newDoc = await createDocument('untitled doc');
          setCurrentDocument(newDoc);
          setDocumentTitle(newDoc.title);
          setEditorContent(newDoc.content || '');
        } else {
          // Guest mode - just set up local state
          setDocumentTitle('untitled doc');
          setEditorContent('');
        }
        
        setIsInitialized(true);
      } catch (error) {
        console.error('Error initializing document:', error);
        // Fallback to guest mode
        setDocumentTitle('untitled doc');
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



  // Remove auto-hide functionality for AI hint - keep it permanent
  // No useEffect needed for hiding the hint

  // App Map functionality moved to Home section - remove from header
  // This will be accessible through the Home button for better organization

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
      {/* Simplified Header - MVP Version with Viral-Focused Priority */}
      <div className="workspace-header">
        {/* Header Controls Container - Reordered for viral growth */}
        <div className="header-buttons-container">
          {/* Story Generator Button - PRIMARY POSITION for viral content creation */}
          <button
            className="nav-action-button primary"
            onClick={() => setShowStoryGenerator(true)}
            type="button"
            aria-label="Generate AI story"
            title="AI Story Generator - Create viral micro-stories"
          >
            <span className="nav-action-icon" aria-hidden="true">✨</span>
            <span className="nav-action-text">Story Generator</span>
          </button>

          {/* Home Button - SECOND POSITION for secondary features */}
          <button
            onClick={() => setShowDocumentManager(true)}
            className="nav-action-button"
            title="Home - Documents, App Map, and more"
          >
            <span className="nav-action-icon" aria-hidden="true">🏠</span>
            <span className="nav-action-text">Home</span>
          </button>

          {/* Auth Button - FINAL POSITION for conversion */}
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
              className="nav-action-button"
              type="button"
              aria-label="Sign in"
              title="Sign In"
            >
              <span className="nav-action-icon" aria-hidden="true">👤</span>
              <span className="nav-action-text">Sign In</span>
            </button>
          )}
        </div>
        
        {/* Document Title - Simplified and concise */}
        <div className="title-section">
          <input
            type="text"
            value={documentTitle}
            onChange={(e) => handleTitleChange(e.target.value)}
            className="document-title-input"
            placeholder="untitled doc"
          />
        </div>
        
        {/* MVP Controls - Streamlined essentials without Copy button */}
        <div className="workspace-controls">
          {/* Chat Toggle Button - Always visible for better UX */}
          <button
            onClick={toggleChat}
            className="copy-content-btn"
            title={isChatVisible ? "Hide AI Assistant" : "Show AI Assistant"}
            aria-label={isChatVisible ? "Hide AI Assistant" : "Show AI Assistant"}
          >
            <span className="copy-icon" aria-hidden="true">💬</span>
            <span className="copy-text">{isChatVisible ? "Hide AI" : "Show AI"}</span>
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
            
            {/* Enhanced AI Discovery Hint - Clean and focused */}
            <div className="bottom-controls">
              <div className="ai-discovery-hint-permanent enhanced">
                💡 Highlight any text for instant AI help
              </div>
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

      {/* Fiction Document Manager Modal - removed, template system deprecated */}

      {/* Story Generator Modal */}
      {showStoryGenerator && (
        <StoryGeneratorModal
          isOpen={showStoryGenerator}
          onClose={() => setShowStoryGenerator(false)}
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