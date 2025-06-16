import React, { useRef, useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Link, useLocation } from 'react-router-dom';
import HighlightableEditor from './components/HighlightableEditor';
import ChatPane from './components/ChatPane';
import Controls from './components/Controls';
import WritingTimer from './components/WritingTimer';
import AuthModal from './components/AuthModal';
import UserProfileModal from './components/UserProfileModal';
import DocumentTitleBar from './components/DocumentTitleBar';
import DocumentHelp from './components/DocumentHelp';
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

// Enhanced navigation component
const Navigation: React.FC = () => {
  const location = useLocation();
  const [showAuthModal, setShowAuthModal] = useState(false);
  const [showProfileModal, setShowProfileModal] = useState(false);
  
  const navItems = [
    { path: '/', label: 'Writer\'s Desk', icon: '✍️' },
    { path: '/manga', label: 'Manga Studio', icon: '🎨' },
    { path: '/voice', label: 'Voice to Text', icon: '🎤' },
  ];

  return (
    <nav className="main-navigation">
      {/* First Row - Brand */}
      <div className="nav-brand-row">
        <div className="nav-brand">
          <h1 className="brand-text">Owen</h1>
          <span className="brand-tagline">Your AI Writing Companion</span>
        </div>
      </div>
      
      {/* Second Row - Navigation Links */}
      <div className="nav-links-row">
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
      </div>

      {/* Authentication Modal */}
      <AuthModal
        isOpen={showAuthModal}
        onClose={() => setShowAuthModal(false)}
        initialMode="signin"
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
      {/* Main Writing Interface - Text content at the very top */}
      <div className={`writing-interface ${isChatOpen ? 'with-chat' : 'editor-only'}`}>
        {/* Main Editor Panel - Text content at the top */}
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
  );
};

export default App;
