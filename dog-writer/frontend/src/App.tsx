import React, { useRef, useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Link, useLocation } from 'react-router-dom';
import HighlightableEditor from './components/HighlightableEditor';
import ChatPane from './components/ChatPane';
import AuthModal from './components/AuthModal';
import UserProfileModal from './components/UserProfileModal';
import DocumentTitleBar from './components/DocumentTitleBar';
import DocumentHelp from './components/DocumentHelp';
import DocumentsPage from './pages/DocumentsPage';
import DocumentEditor from './pages/DocumentEditor';
import './App.css';
import { AppProvider, useAppContext } from './contexts/AppContext';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import { useTheme } from './contexts/ThemeContext';
import { ThemeProvider } from './contexts/ThemeContext';

// Top Navigation Bar with Documents, Settings, Auth in top right
const TopNavigation: React.FC = () => {
  const location = useLocation();
  const { isAuthenticated, user, logout } = useAuth();
  const { setShowAuthModal, setAuthMode } = useAppContext();
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

// Full Writers Desk with single-pane layout and toggleable chat
const WritersDesk: React.FC = () => {
  const [isChatOpen, setIsChatOpen] = useState(false);
  const [editorContent, setEditorContent] = useState('');
  const [selection, setSelection] = useState<{ top: number; left: number; text: string } | null>(null);
  const editorRef = useRef<HTMLDivElement>(null);

  const toggleChat = () => {
    setIsChatOpen(!isChatOpen);
  };

  // Handle highlighted text for chat integration
  useEffect(() => {
    const handleHighlightedTextForChat = (event: CustomEvent) => {
      const { text, requestType, highlightId, color } = event.detail;
      
      // Open chat if not already open
      if (!isChatOpen) {
        setIsChatOpen(true);
      }

      // Create appropriate message based on request type
      let message = '';
      switch (requestType) {
        case 'feedback':
          message = `Please provide feedback on this text: "${text}"`;
          break;
        case 'improve':
          message = `How can I improve this text: "${text}"`;
          break;
        case 'question':
          message = `I have a question about this text: "${text}"`;
          break;
        default:
          message = `Please analyze this text: "${text}"`;
      }

      // Send message to chat after a brief delay to ensure chat is open
      setTimeout(() => {
        const chatEvent = new CustomEvent('sendChatMessage', {
          detail: { message, highlightedText: text, highlightId }
        });
        window.dispatchEvent(chatEvent);
      }, 100);
    };

    window.addEventListener('highlightedTextForChat', handleHighlightedTextForChat as EventListener);

    return () => {
      window.removeEventListener('highlightedTextForChat', handleHighlightedTextForChat as EventListener);
    };
  }, [isChatOpen]);

  const handleTextHighlighted = (selectedText: string) => {
    const sel = window.getSelection();
    if (!sel || sel.rangeCount === 0 || !selectedText) {
      setSelection(null);
      return;
    }
    const range = sel.getRangeAt(0);
    const rect = range.getBoundingClientRect();
    
    if (editorRef.current) {
      const editorRect = editorRef.current.getBoundingClientRect();
      
      // Calculate position relative to editor
      let top = rect.top - editorRect.top + rect.height + 8; // Add 8px gap
      let left = rect.left - editorRect.left + rect.width / 2;
      
      // Bounds checking to prevent overlap with chat panel
      const editorWidth = editorRect.width;
      const editorHeight = editorRect.height;
      
      // If chat is open, keep button within left 60% of editor to avoid chat overlap
      if (isChatOpen) {
        const maxLeft = editorWidth * 0.6 - 80; // 80px for button width
        left = Math.min(left, maxLeft);
      }
      
      // Keep button within editor bounds
      left = Math.max(80, Math.min(left, editorWidth - 80)); // 80px margin from edges
      top = Math.max(10, Math.min(top, editorHeight - 50)); // 50px margin from bottom
      
      setSelection({
        top,
        left,
        text: selectedText,
      });
    }
  };
  
  const handleAiSubmit = () => {
    // Logic to submit the selection.text to the AI
    console.log('Submitting to AI:', selection?.text);
    setSelection(null); // Hide button after submit
    setIsChatOpen(true); // Open chat
  };

  // Hide floating button when chat is open and user might be typing
  const shouldShowFloatingButton = selection;

  return (
    <div className="writers-desk">
      {/* Main Writing Interface - Clean and focused */}
      <div className={`writing-interface ${isChatOpen ? 'with-chat' : 'editor-only'}`}>
        {/* Main Editor Panel - Larger writing space */}
        <div className="editor-panel">
          {/* Document Title Bar */}
          <DocumentTitleBar />
          
          {/* Document Help Banner */}
          <DocumentHelp />
          
          <div className="editor-container" ref={editorRef}>
            <HighlightableEditor
              content={editorContent}
              onChange={setEditorContent}
              onTextHighlighted={handleTextHighlighted}
            />
             {shouldShowFloatingButton && (
              <div 
                className="floating-ai-button" 
                style={{ top: selection.top, left: selection.left }}
                onClick={handleAiSubmit}
              >
                Ask AI
              </div>
            )}
          </div>
        </div>

        {/* Sliding Chat Panel */}
        <div className={`chat-panel ${isChatOpen ? 'open' : 'closed'}`}>
          <ChatPane />
        </div>
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
      </button>
    </div>
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
  const { showAuthModal, authMode, setShowAuthModal } = useAppContext();

  useEffect(() => {
    document.body.className = `theme-${theme}`;
  }, [theme]);

  return (
    <Router>
      <AppLayout>
        <Routes>
          <Route path="/" element={<WritersDesk />} />
          <Route path="/documents" element={<DocumentsPage />} />
          <Route path="/editor/:documentId" element={<DocumentEditor />} />
          <Route path="*" element={<WritersDesk />} />
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
      <AuthProvider>
        <AppProvider>
          <AppContent />
        </AppProvider>
      </AuthProvider>
    </ThemeProvider>
  );
};

export default App;
