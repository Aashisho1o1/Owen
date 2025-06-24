import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { AppProvider } from './contexts/AppContext';
import DocumentEditor from './pages/DocumentEditor';
import DocumentsPage from './pages/DocumentsPage';
import WritingWorkspace from './components/WritingWorkspace';
import AuthModal from './components/AuthModal';
import UserProfileModal from './components/UserProfileModal';
import { useAuth } from './contexts/AuthContext';
import './App.css';

// Auth Float Component - now used for ALL devices
const AuthFloat: React.FC = () => {
  const { user, isAuthenticated } = useAuth();
  const [showAuthModal, setShowAuthModal] = React.useState(false);
  const [showProfileModal, setShowProfileModal] = React.useState(false);

  const handleAuthClick = () => {
    if (isAuthenticated) {
      setShowProfileModal(true);
    } else {
      setShowAuthModal(true);
    }
  };

  return (
    <>
      <div className="auth-float">
        {isAuthenticated ? (
          <button
            className="profile-button"
            onClick={handleAuthClick}
            aria-label="User Profile"
          >
            <div className="profile-avatar">
              {user?.display_name?.charAt(0)?.toUpperCase() || user?.email?.charAt(0)?.toUpperCase() || '?'}
            </div>
          </button>
        ) : (
          <button
            className="auth-button"
            onClick={handleAuthClick}
          >
            Sign In
          </button>
        )}
      </div>

      <AuthModal
        isOpen={showAuthModal}
        onClose={() => setShowAuthModal(false)}
      />

      <UserProfileModal
        isOpen={showProfileModal}
        onClose={() => setShowProfileModal(false)}
      />
    </>
  );
};

// Simplified App Layout without top navigation
const AppLayout: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  return (
    <div className="app-layout">
      <AuthFloat />
      <main className="app-main">
        {children}
      </main>
    </div>
  );
};

const AppContent: React.FC = () => {
  return (
    <AppLayout>
      <Routes>
        {/* Default route - direct to writing workspace */}
        <Route path="/" element={<WritingWorkspace />} />
        {/* Documents management page */}
        <Route path="/documents" element={<DocumentsPage />} />
        {/* Individual document editor */}
        <Route path="/document/:documentId" element={<DocumentEditor />} />
      </Routes>
    </AppLayout>
  );
};

const App: React.FC = () => {
  return (
    <AppProvider>
      <Router>
        <AppContent />
      </Router>
    </AppProvider>
  );
};

export default App;
