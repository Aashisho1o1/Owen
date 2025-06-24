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
