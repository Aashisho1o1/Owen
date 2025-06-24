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
