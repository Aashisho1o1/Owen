import React, { useState, useEffect, useCallback } from 'react';
import HighlightableEditor from './HighlightableEditor';
import ChatPane from './ChatPane';
import DocumentManager from './DocumentManager';
import { StoryGeneratorModal } from './StoryGeneratorModal';
import { useDocuments } from '../hooks/useDocuments';
import { useAuth } from '../contexts/AuthContext';
import { useChatContext } from '../contexts/ChatContext';
import { useEditorContext } from '../contexts/EditorContext';
import AuthModal from './AuthModal';
import UserProfileModal from './UserProfileModal';
import { Document } from '../services/api/types'; // ✅ ADDED: Import Document type
// Voice consistency analysis is now handled in HighlightableEditor
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
  const { isAuthenticated, isLoading: authLoading } = useAuth(); // Add authLoading
  const { isChatVisible, toggleChat } = useChatContext();
  const { editorContent, setEditorContent } = useEditorContext();
  const {
    updateTitle,
    updateContent, // Add updateContent to connect editor changes to document management
    saveNow,
    isSaving,
    lastSaved,
    hasUnsavedChanges,
    currentDocument,
    setCurrentDocument,
    // ✅ REMOVED: getDocument - no longer needed
  } = useDocuments();

  // Auth state for header
  const { user } = useAuth();
  const [showAuthModal, setShowAuthModal] = useState(false);
  const [showProfileModal, setShowProfileModal] = useState(false);

  const [documentTitle, setDocumentTitle] = useState('untitled doc');
  const [isLoading, setIsLoading] = useState(true);
  const [isInitialized, setIsInitialized] = useState(false);
  
  // FIXED: Connect editor content changes to document management
  const handleEditorContentChange = useCallback((content: string) => {
    setEditorContent(content); // Update local editor state
    if (isAuthenticated && currentDocument) {
      updateContent(content); // Update document management state
    }
  }, [isAuthenticated, currentDocument, updateContent, setEditorContent]);

  // Fiction Document Manager state
  const [showDocumentManager, setShowDocumentManager] = useState(false);
  
  // Story Generator state
  const [showStoryGenerator, setShowStoryGenerator] = useState(false);

  // Initialize document on component mount - FIXED: Don't create new documents automatically
  useEffect(() => {
    const initializeDocument = async () => {
      try {
        setIsLoading(true);
        
        if (isAuthenticated) {
          // CRITICAL FIX: Check if there's already a current document
          // Only create new document if user explicitly wants one
          if (!currentDocument) {
            // Start with empty state - let user choose to create or open existing
            setDocumentTitle('');
            setEditorContent('');
            console.log('📋 WritingWorkspace: Ready for document selection');
          } else {
            // Use existing current document
            setDocumentTitle(currentDocument.title);
            setEditorContent(currentDocument.content || '');
            console.log('📋 WritingWorkspace: Loaded existing document:', currentDocument.title);
          }
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

    // Only initialize when auth is not loading and not already initialized
    if (!authLoading && !isInitialized) {
      initializeDocument();
    }
  }, [isAuthenticated, authLoading, isInitialized, currentDocument, setEditorContent]); // FIXED: Add all dependencies

  // CRITICAL FIX: Simplified state sync - only sync when document changes, not on every content update
  useEffect(() => {
    if (currentDocument) {
      // Only sync when switching to a different document
      const isNewDocument = currentDocument.content !== editorContent;
      const hasNoUserContent = !editorContent || editorContent.trim().length === 0;
      
      // Only overwrite editor content if:
      // 1. It's a genuinely different document, AND
      // 2. User hasn't typed anything yet, OR the document has actual content
      if (isNewDocument && (hasNoUserContent || currentDocument.content)) {
        console.log('📝 Loading document content into editor:', {
          documentId: currentDocument.id,
          documentTitle: currentDocument.title,
          contentLength: currentDocument.content?.length || 0
        });
        setEditorContent(currentDocument.content || '');
        setDocumentTitle(currentDocument.title);
      }
    }
  }, [currentDocument, editorContent, setEditorContent, setDocumentTitle]); // FIXED: Include currentDocument object

  // Handle auth modal - prevent opening when already authenticated
  const handleAuthModalOpen = () => {
    // Prevent opening login modal if user is already authenticated
    if (isAuthenticated || authLoading) {
      console.log('🔐 Preventing login modal - user already authenticated or auth loading');
      return;
    }
    setShowAuthModal(true);
  };

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

  // ✅ FIXED: Handle document selection from Fiction Document Manager
  const handleDocumentSelect = (document: Document) => {
    console.log('📋 WritingWorkspace: Selecting document:', {
      documentId: document.id,
      title: document.title,
      wordCount: document.word_count,
      updatedAt: document.updated_at
    });
    
    // ✅ The document from DocumentManager is ALREADY complete with all fields!
    // This includes real timestamps, word_count, user_id, etc.
    // No need for extra API call - just use it directly!
    setCurrentDocument(document);
    
    // ✅ Update local editor state to match the document
    setDocumentTitle(document.title);
    setEditorContent(document.content || '');
    
    // Close the modal
    setShowDocumentManager(false);
    
    console.log('✅ WritingWorkspace: Document loaded successfully');
  };

  // Handle returning to writing space from Document Manager
  const handleReturnToWriting = () => {
    setShowDocumentManager(false);
  };


  // Remove auto-hide functionality for AI hint - keep it permanent
  // No useEffect needed for hiding the hint

  // App Map functionality moved to Home section - remove from header
  // This will be accessible through the Home button for better organization

  // Show loading state during both app initialization and auth loading
  if (isLoading || authLoading) {
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

          {/* Auth Button - FINAL POSITION for conversion - IMPROVED LOGIC */}
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
              onClick={handleAuthModalOpen}
              className="nav-action-button"
              type="button"
              aria-label="Sign in"
              title="Sign In"
              disabled={authLoading} // Disable during auth loading
            >
              <span className="nav-action-icon" aria-hidden="true">👤</span>
              <span className="nav-action-text">{authLoading ? 'Loading...' : 'Sign In'}</span>
            </button>
          )}
        </div>
        
        {/* IMPROVED: Document Title with better context */}
        <div className="title-section">
          <input
            type="text"
            value={documentTitle}
            onChange={(e) => handleTitleChange(e.target.value)}
            className="document-title-input"
            placeholder={currentDocument ? "Untitled Document" : (isAuthenticated ? "New Document (click Home to save)" : "Guest Draft")}
            title={currentDocument ? 
              `Editing "${currentDocument.title}" (ID: ${currentDocument.id})` : 
              isAuthenticated ? 
                "Create a new document from Home to save this content" : 
                "Sign in and create a document to save your work"
            }
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

          {/* IMPROVED: Save Status with better user feedback */}
          {isAuthenticated && (
            <div className="save-status">
              {isSaving && <span className="status-saving">💾 Saving...</span>}
              {!isSaving && hasUnsavedChanges && (
                <button onClick={handleSaveNow} className="save-now-btn" title="Click to save your changes">
                  💾 Save Now
                </button>
              )}
              {!isSaving && !hasUnsavedChanges && lastSaved && currentDocument && (
                <span className="status-saved" title={`Document "${currentDocument.title}" saved ${formatLastSaved()}`}>
                  ✅ Saved {formatLastSaved()}
                </span>
              )}
              {!isSaving && !currentDocument && (
                <span className="status-unsaved" title="Create a new document or open an existing one to save your work">
                  📝 Unsaved draft
                </span>
              )}
            </div>
          )}
          
          {/* IMPROVED: Guest mode indicator */}
          {!isAuthenticated && (
            <div className="save-status guest-status">
              <span className="status-guest" title="Sign in to save and manage your documents">
                👤 Guest mode - Sign in to save
              </span>
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
              content={editorContent}
              onChange={handleEditorContentChange}
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

      {/* Document Manager Modal */}
      {showDocumentManager && (
        <DocumentManager
          onDocumentSelect={handleDocumentSelect}
          onClose={() => setShowDocumentManager(false)}
          onReturnToWriting={handleReturnToWriting}
        />
      )}

      {/* Story Generator Modal */}
      {showStoryGenerator && (
        <StoryGeneratorModal
          isOpen={showStoryGenerator}
          onClose={() => setShowStoryGenerator(false)}
        />
      )}

      {/* Auth Modals - Only show when not authenticated */}
      {!isAuthenticated && showAuthModal && (
        <AuthModal
          isOpen={showAuthModal}
          onClose={() => setShowAuthModal(false)}
          initialMode="signin"
        />
      )}
      
      {isAuthenticated && showProfileModal && (
        <UserProfileModal
          isOpen={showProfileModal}
          onClose={() => setShowProfileModal(false)}
        />
      )}
    </div>
  );
};

export default WritingWorkspace;