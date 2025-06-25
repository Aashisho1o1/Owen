import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { AppProvider } from './contexts/AppContext';
import DocumentEditor from './pages/DocumentEditor';
import DocumentsPage from './pages/DocumentsPage';
import { WritingWorkspace } from './components/WritingWorkspace';
import AuthModal from './components/AuthModal';
import UserProfileModal from './components/UserProfileModal';
import { useAuth } from './contexts/AuthContext';
import './App.css';
import './styles/chat-input-width-fix.css';

// Light Theme Override Styles to fix dark backgrounds
const lightThemeOverrides = `
/* Force light theme overrides - Fix dark background issues */
:root {
  --bg-primary: #fefefe !important;
  --bg-secondary: #ffffff !important;
  --bg-elevated: #fefefe !important;
  --bg-accent: #f9fafb !important;
  --text-primary: #1f2937 !important;
  --text-secondary: #374151 !important;
  --text-muted: #6b7280 !important;
  --border-light: #e5e7eb !important;
  --border-medium: #d1d5db !important;
  --border-strong: #9ca3af !important;
}

body, .app, .app-main, .writing-workspace, .workspace-header, .workspace-content,
.editor-section, .editor-container, .chat-section, .chat-panel-container,
.chat-header, .chat-title, .highlightable-editor, .editor-wrapper {
  background: #fefefe !important;
  background-color: #fefefe !important;
  color: #1f2937 !important;
}

.highlightable-editor, .ProseMirror {
  background: #ffffff !important;
  background-color: #ffffff !important;
  color: #1f2937 !important;
}

.chat-title h1, .chat-title h2, .chat-title h3, .chat-title h4,
.chat-title span, .chat-title div {
  background: transparent !important;
  background-color: transparent !important;
  color: #1f2937 !important;
}

.theme-dark {
  --bg-primary: #fefefe !important;
  --bg-secondary: #ffffff !important;
  --bg-elevated: #fefefe !important;
  --text-primary: #1f2937 !important;
}

/* ============= CRITICAL CHAT TEXT VISIBILITY FIXES ============= */
/* Force ALL chat content to be readable with dark text on light backgrounds */

.chat-panel-container,
.chat-panel-container *,
.messages-container,
.messages-container *,
.message,
.message *,
.ai-message,
.ai-message *,
.chat-welcome,
.chat-welcome *,
.welcome-message,
.welcome-message *,
.conversation-starters,
.conversation-starters *,
.starter-questions,
.starter-questions *,
div[class*="chat"],
div[class*="chat"] *,
div[class*="message"],
div[class*="message"] * {
  background-color: #ffffff !important;
  color: #1f2937 !important;
}

/* EXCEPTION: User messages keep blue background with white text */
.user-message .message-content,
.user-message .message-content *,
.user-message .message-content p,
.user-message .message-content span,
.user-message .message-content div {
  background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%) !important;
  color: white !important;
}

/* AI Messages - Explicit white background and dark text */
.ai-message .message-content,
.ai-message .message-content *,
.ai-message .message-content p,
.ai-message .message-content span,
.ai-message .message-content div,
.ai-message .message-content h1,
.ai-message .message-content h2,
.ai-message .message-content h3,
.ai-message .message-content h4,
.ai-message .message-content h5,
.ai-message .message-content h6 {
  background: #ffffff !important;
  color: #1f2937 !important;
  border: 1px solid #e5e7eb !important;
}

/* Chat Header and Title - Maximum specificity */
.chat-header,
.chat-header *,
.chat-title,
.chat-title *,
.chat-title h1,
.chat-title h2,
.chat-title h3,
.chat-title h4,
.chat-title span,
.chat-title div {
  background: #fefefe !important;
  background-color: #fefefe !important;
  color: #1f2937 !important;
}

/* Welcome Messages and Initial AI Content */
.chat-welcome,
.chat-welcome *,
.welcome-message,
.welcome-message *,
.starter-question-button,
.starter-question-button * {
  background: #ffffff !important;
  color: #1f2937 !important;
  border: 1px solid #e5e7eb !important;
}

/* Chat Input Elements */
.chat-input-container,
.chat-input-container *,
.chat-textarea,
.chat-textarea *,
.chat-input-form,
.chat-input-form * {
  background: #ffffff !important;
  color: #1f2937 !important;
  border-color: #d1d5db !important;
}

/* Final override - Maximum specificity for AI messages */
body .chat-panel-container .messages-container .message.ai-message .message-content,
body .chat-panel-container .messages-container .message.ai-message .message-content *,
body .chat-panel-container .chat-welcome,
body .chat-panel-container .chat-welcome *,
body .chat-panel-container .welcome-message,
body .chat-panel-container .welcome-message * {
  background: #ffffff !important;
  background-color: #ffffff !important;
  color: #1f2937 !important;
}
`;

// Clean Auth Float Component for MVP - Top right corner
const AuthFloat: React.FC = () => {
  const { user, isAuthenticated } = useAuth();
  const [showAuthModal, setShowAuthModal] = React.useState(false);
  const [showProfileModal, setShowProfileModal] = React.useState(false);

  if (isAuthenticated && user) {
    return (
      <>
        <div className="auth-float auth-float-mvp">
          <button
            onClick={() => setShowProfileModal(true)}
            className="profile-button profile-button-mvp"
            title="User Profile"
          >
            <div className="profile-avatar profile-avatar-mvp">
              {user.display_name?.charAt(0)?.toUpperCase() || user.email?.charAt(0)?.toUpperCase() || 'U'}
            </div>
          </button>
        </div>
        {showProfileModal && (
          <UserProfileModal
            isOpen={showProfileModal}
            onClose={() => setShowProfileModal(false)}
          />
        )}
      </>
    );
  }

  return (
    <>
      <div className="auth-float auth-float-mvp">
        <button
          onClick={() => setShowAuthModal(true)}
          className="auth-button auth-button-mvp"
          title="Sign In"
        >
          Sign In
        </button>
      </div>
      {showAuthModal && (
        <AuthModal
          isOpen={showAuthModal}
          onClose={() => setShowAuthModal(false)}
          initialMode="signin"
        />
      )}
    </>
  );
};

// Clean App Layout for MVP
const AppLayout: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <div className="app-layout app-layout-mvp">
    <style dangerouslySetInnerHTML={{ __html: lightThemeOverrides }} />
    {children}
    <AuthFloat />
  </div>
);

// Main App Content
const AppContent: React.FC = () => {
  return (
    <AppLayout>
      <div className="app-main app-main-mvp">
        <Routes>
          {/* MVP Route - Direct to Writing Workspace */}
          <Route path="/" element={<WritingWorkspace />} />
          
          {/* Hidden routes for later use */}
          <Route path="/documents" element={<DocumentsPage />} />
          <Route path="/document/:documentId" element={<DocumentEditor />} />
        </Routes>
      </div>
    </AppLayout>
  );
};

// Root App Component
const App: React.FC = () => {
  return (
    <Router>
      <AppProvider>
        <AppContent />
      </AppProvider>
    </Router>
  );
};

export default App;
