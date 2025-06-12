import React, { useRef, useState } from 'react';
import { BrowserRouter as Router, Routes, Route, Link, useLocation } from 'react-router-dom';
import { AppProvider } from './contexts/AppContext';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import { ThemeProvider } from './contexts/ThemeContext';
import Editor from './components/Editor';
import ChatPane from './components/ChatPane';
import Controls from './components/Controls';
import WritingTimer from './components/WritingTimer';
import AuthModal from './components/AuthModal';
import UserProfileModal from './components/UserProfileModal';
import MangaStudioPage from './pages/MangaStudioPage';
import './App.css';

// Voice to Text Page
const VoiceToTextPage: React.FC = () => {
  return (
    <div className="voice-page">
      <div className="voice-controls">
        <div style={{ padding: '40px 20px', textAlign: 'center' }}>
          <div style={{ padding: '20px', background: '#f8fafc', borderRadius: '8px', marginBottom: '20px' }}>
            <h3>🎤 Voice Recognition</h3>
            <p>Advanced voice-to-text functionality coming soon...</p>
            <p>Will include real-time transcription and voice commands</p>
          </div>
        </div>
      </div>
    </div>
  );
};

// Enhanced navigation component with authentication
const Navigation: React.FC = () => {
  const location = useLocation();
  const { isAuthenticated, user, isLoading } = useAuth();
  const [showAuthModal, setShowAuthModal] = useState(false);
  const [showProfileModal, setShowProfileModal] = useState(false);
  const [authMode, setAuthMode] = useState<'login' | 'register'>('login');
  
  const navItems = [
    { path: '/', label: 'Writer\'s Desk', icon: '✍️' },
    { path: '/manga', label: 'Manga Studio', icon: '🎨' },
    { path: '/voice', label: 'Voice to Text', icon: '🎤' },
  ];

  const handleAuthClick = (mode: 'login' | 'register') => {
    setAuthMode(mode);
    setShowAuthModal(true);
  };

  const handleProfileClick = () => {
    setShowProfileModal(true);
  };

  return (
    <nav className="main-navigation">
      <div className="nav-brand">
        <h1 className="brand-text">Owen</h1>
        <span className="brand-tagline">AI Writing Companion</span>
      </div>
      
      <div className="nav-links">
        {navItems.map((item) => (
          <Link
            key={item.path}
            to={item.path}
            className={`nav-link ${location.pathname === item.path ? 'active' : ''}`}
          >
            <span className="nav-icon">{item.icon}</span>
            <span className="nav-label">{item.label}</span>
          </Link>
        ))}
      </div>

      {/* Authentication section */}
      <div className="nav-auth">
        {isLoading ? (
          <div className="nav-auth-loading">
            <div className="loading-spinner"></div>
          </div>
        ) : isAuthenticated && user ? (
          // Authenticated user menu
          <div className="nav-user-menu">
            <button 
              className="nav-user-button"
              onClick={handleProfileClick}
              title={`Signed in as ${user.display_name || user.username}`}
            >
              <div className="nav-user-avatar">
                {(user.display_name || user.username).charAt(0).toUpperCase()}
              </div>
              <span className="nav-user-name">
                {user.display_name || user.username}
              </span>
            </button>
          </div>
        ) : (
          // Unauthenticated user buttons
          <div className="nav-auth-buttons">
            <button
              className="nav-auth-button secondary"
              onClick={() => handleAuthClick('login')}
            >
              Sign In
            </button>
            <button
              className="nav-auth-button primary"
              onClick={() => handleAuthClick('register')}
            >
              Get Started
            </button>
          </div>
        )}
      </div>

      {/* Authentication Modal */}
      <AuthModal
        isOpen={showAuthModal}
        onClose={() => setShowAuthModal(false)}
        initialMode={authMode}
      />

      {/* User Profile Modal */}
      <UserProfileModal
        isOpen={showProfileModal}
        onClose={() => setShowProfileModal(false)}
      />
    </nav>
  );
};

// Full Writers Desk with single-pane layout and toggleable chat
const WritersDesk: React.FC = () => {
  const [isChatOpen, setIsChatOpen] = useState(false);
  const [editorContent, setEditorContent] = useState('');

  const toggleChat = () => {
    setIsChatOpen(!isChatOpen);
  };

  const handleTextHighlighted = (selectedText: string) => {
    console.log('Text highlighted:', selectedText);
  };

  return (
    <div className="writers-desk">
      {/* Main Writing Interface - Text content at the very top */}
      <div className={`writing-interface ${isChatOpen ? 'with-chat' : 'editor-only'}`}>
        {/* Main Editor Panel - Text content at the top */}
        <div className="editor-panel">
          <div className="editor-container">
            <Editor 
              content={editorContent} 
              onChange={setEditorContent} 
              onTextHighlighted={handleTextHighlighted} 
            />
          </div>
        </div>

        {/* Sliding Chat Panel */}
        <div className={`chat-panel ${isChatOpen ? 'open' : 'closed'}`}>
          <ChatPane />
        </div>
      </div>

      {/* Floating Controls - Left Sidebar */}
      <div className="controls-sidebar">
        <Controls />
      </div>

      {/* Floating Chat Toggle Button */}
      <button 
        className={`chat-toggle-button ${isChatOpen ? 'active' : ''}`}
        onClick={toggleChat}
        title={isChatOpen ? 'Close AI Chat' : 'Open AI Chat'}
      >
        <svg 
          xmlns="http://www.w3.org/2000/svg" 
          width="20" 
          height="20" 
          viewBox="0 0 24 24" 
          fill="none" 
          stroke="currentColor" 
          strokeWidth="2" 
          strokeLinecap="round" 
          strokeLinejoin="round"
        >
          <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path>
        </svg>
        {isChatOpen ? 'Close Chat' : 'AI Chat'}
      </button>
    </div>
  );
};

const AppLayout: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const editorRef = useRef<HTMLDivElement>(null);

  return (
    <div className="app-layout">
      <Navigation />
      
      <main className="main-content">
        <div className="content-wrapper">
          {children}
        </div>
        
        {/* Writing Timer - Floating */}
        <div className="writing-timer-float">
          <WritingTimer editorRef={editorRef} />
        </div>
      </main>
    </div>
  );
};

const App: React.FC = () => {
  return (
    <ThemeProvider>
      <AuthProvider>
        <AppProvider>
          <Router>
            <AppLayout>
              <Routes>
                <Route path="/" element={<WritersDesk />} />
                <Route path="/manga" element={<MangaStudioPage />} />
                <Route path="/voice" element={<VoiceToTextPage />} />
                <Route path="*" element={<WritersDesk />} />
              </Routes>
            </AppLayout>
          </Router>
        </AppProvider>
      </AuthProvider>
    </ThemeProvider>
  );
};

export default App;
