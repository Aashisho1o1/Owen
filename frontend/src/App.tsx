import React, { useRef, useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate, Link, useLocation } from 'react-router-dom';
import WritingWorkspace from './components/WritingWorkspace';
import AuthModal from './components/AuthModal';
import UserProfileModal from './components/UserProfileModal';
import DocumentsPage from './pages/DocumentsPage';
import DocumentEditor from './pages/DocumentEditor';
import './App.css';
import { AppProvider } from './contexts/AppContext';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import { useUIContext } from './contexts/UIContext';
import { ThemeProvider, useTheme } from './contexts/ThemeContext';
import { DocumentThemeProvider } from './contexts/DocumentThemeContext';

// Top Navigation Bar with Documents, Settings, Auth in top right
const TopNavigation: React.FC = () => {
  const location = useLocation();
  const { isAuthenticated, user } = useAuth();
  const { setShowAuthModal, setAuthMode } = useUIContext();
  const [showProfileModal, setShowProfileModal] = useState(false);

  const handleAuthClick = () => {
    if (isAuthenticated) {
      setShowProfileModal(true);
    } else {
      setAuthMode('signin');
      setShowAuthModal(true);
    }
  };

  const handleSignUpClick = () => {
    setAuthMode('signup');
    setShowAuthModal(true);
  };

  return (
    <nav className="top-navigation">
      <div className="nav-container">
        {/* Left side - Brand */}
        <div className="nav-brand">
          <Link to="/" className="brand-link">
            <h1 className="brand-text">Owen</h1>
            <span className="brand-tagline">AI Writing Companion</span>
          </Link>
        </div>
        
        {/* Right side - Navigation items */}
        <div className="nav-actions">
          <Link 
            to="/documents" 
            className={`nav-action-button ${location.pathname === '/documents' ? 'active' : ''}`}
          >
            📄 Documents
          </Link>
          
          <button className="nav-action-button" onClick={() => setShowProfileModal(true)}>
            ⚙️ Settings
          </button>
          
          {isAuthenticated ? (
            <div className="user-menu">
              <button className="nav-action-button user-button" onClick={handleAuthClick}>
                👤 {user?.email || 'Profile'}
              </button>
            </div>
          ) : (
            <div className="auth-buttons">
              <button className="nav-action-button" onClick={handleAuthClick}>
                Sign In
              </button>
              <button className="nav-action-button primary" onClick={handleSignUpClick}>
                Sign Up
              </button>
            </div>
          )}
        </div>
      </div>

      {/* User Profile Modal */}
      <UserProfileModal
        isOpen={showProfileModal}
        onClose={() => setShowProfileModal(false)}
      />
    </nav>
  );
};

// App Layout with top navigation
const AppLayout: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  return (
    <div className="app-layout">
      <TopNavigation />
      <main className="app-main">
        {children}
      </main>
    </div>
  );
};

const AppContent: React.FC = () => {
  const { theme } = useTheme();
  const { showAuthModal, authMode, setShowAuthModal } = useUIContext();

  useEffect(() => {
    document.body.className = `theme-${theme}`;
  }, [theme]);

  return (
    <Router>
      <AppLayout>
        <Routes>
          <Route path="/" element={<WritingWorkspace />} />
          <Route path="/documents" element={<DocumentsPage />} />
          <Route path="/editor/:documentId" element={<DocumentEditor />} />
          <Route path="*" element={<WritingWorkspace />} />
        </Routes>
      </AppLayout>
      <AuthModal
        isOpen={showAuthModal}
        onClose={() => setShowAuthModal(false)}
        initialMode={authMode}
      />
    </Router>
  );
};

const App: React.FC = () => {
  return (
    <ThemeProvider>
      <DocumentThemeProvider>
        <AuthProvider>
          <AppProvider>
            <AppContent />
          </AppProvider>
        </AuthProvider>
      </DocumentThemeProvider>
    </ThemeProvider>
  );
};

export default App;
