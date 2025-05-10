/*
# REFACTORING PLAN

This App.tsx file is too large and should be split into smaller, focused components:

1. Create a new `/hooks` directory for custom hooks:
   - `useChat.ts` - Extract chat-related state and API calls
   - `useEditor.ts` - Extract editor state management
   - `useApiHealth.ts` - Handle API health checking

2. Move layout components to their own files:
   - `components/layout/AppLayout.tsx`
   - `components/layout/ApiErrorBanner.tsx`

3. Create a Context provider for shared state:
   - `contexts/AppContext.tsx` - Manage author persona, help focus, LLM selection
   - This would remove prop drilling throughout the component tree

4. Update main App.tsx to be a thin shell that:
   - Sets up routing
   - Provides context
   - Handles top-level layout

This refactoring will improve:
- Code organization and readability
- Reusability through custom hooks
- Testability of individual components
- Performance through better component isolation
*/

import React from 'react';
import { Routes, Route, Link, Outlet } from 'react-router-dom';
import Editor from './components/Editor';
import ChatPane from './components/ChatPane';
import Controls from './components/Controls';
import MangaStudioPage from './pages/MangaStudioPage';
import VoiceNotesPage from './pages/VoiceNotesPage';
import './App.css';
import { useAppContext } from './contexts/AppContext';

// Main layout component that includes header and controls
const AppLayout: React.FC = () => {
  const { 
    apiGlobalError 
  } = useAppContext();

  return (
    <>
      <header className="app-header">
        <h1>Owen</h1>
        <nav className="app-nav">
          <Link to="/">Writer's Desk</Link>
          <Link to="/manga">Manga Studio</Link>
          <Link to="/voice-notes">Voice Notes</Link>
        </nav>
      </header>
      <Controls />
      {apiGlobalError && (
        <div className="api-error-banner global-api-error">
          <p>{apiGlobalError}</p>
        </div>
      )}
      <Outlet />
    </>
  );
};

// Component for the main Writer's Desk (Editor + Chat)
const WritersDesk: React.FC = () => {
  const {
    editorContent,
    setEditorContent,
    handleTextHighlighted,
    chatApiError
  } = useAppContext();

  return (
    <main className="app-content">
      <div className="editor-pane">
        <Editor 
          content={editorContent} 
          onChange={setEditorContent}
          onTextHighlighted={handleTextHighlighted}
        />
      </div>
      <div className="chat-and-manga-pane">
        {chatApiError && (
          <div className="api-error-banner chat-api-error">
            <p>{chatApiError}</p>
          </div>
        )}
        <ChatPane />
      </div>
    </main>
  );
};

function App() {
  return (
    <div className="app">
      <Routes>
        <Route path="/" element={<AppLayout />}>
          <Route index element={<WritersDesk />} />
          <Route path="manga" element={<MangaStudioPage />} />
          <Route path="voice-notes" element={<VoiceNotesPage />} />
        </Route>
      </Routes>
      
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap');

        :root {
          --primary: #6366f1;
          --primary-light: #818cf8;
          --primary-dark: #4f46e5;
          --accent-color: #14b8a6;
          --accent-light: #5eead4; 
          --text-primary: #0f172a;
          --text-secondary: #334155;
          --text-tertiary: #64748b;
          --bg-main: #f8fafc;
          --bg-panel: #ffffff;
          --border-color: #e2e8f0;
          --rounded-sm: 0.25rem;
          --rounded-md: 0.375rem;
          --rounded-lg: 0.5rem;
          --shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
          --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
          --font-primary: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;
        }

        * {
          box-sizing: border-box;
          margin: 0;
          padding: 0;
        }

        body {
          font-family: var(--font-primary);
          background-color: var(--bg-main);
          color: var(--text-primary);
        }

        .app {
          height: 100vh;
          overflow: hidden;
          display: flex;
          flex-direction: column;
        }

        .app-header {
          display: flex;
          align-items: center;
          padding: 0.75rem 1.5rem;
          background-color: var(--primary);
          color: white;
          z-index: 10;
        }

        .app-header h1 {
          font-size: 1.5rem;
          font-weight: 600;
          margin-right: 2rem;
        }

        .app-nav {
          display: flex;
          gap: 1.5rem;
        }

        .app-nav a {
          color: rgba(255, 255, 255, 0.85);
          text-decoration: none;
          font-weight: 500;
          font-size: 0.875rem;
          padding: 0.25rem 0.5rem;
          border-radius: var(--rounded-sm);
          transition: all 0.2s;
        }

        .app-nav a:hover {
          color: white;
          background-color: rgba(255, 255, 255, 0.1);
        }

        .app-content {
          display: flex;
          flex: 1;
          overflow: hidden;
        }

        .editor-pane {
          flex: 1;
          max-width: 50%;
          border-right: 1px solid var(--border-color);
          overflow: auto;
        }

        .chat-and-manga-pane {
          flex: 1;
          overflow: auto;
          position: relative;
        }

        .api-error-banner {
          background-color: #fee2e2;
          border-left: 4px solid #ef4444;
          color: #b91c1c;
          padding: 0.75rem 1rem;
          margin-bottom: 1rem;
          font-size: 0.875rem;
          font-weight: 500;
          animation: slideDown 0.3s ease;
        }

        .global-api-error {
          margin: 0.5rem 1rem;
          border-radius: var(--rounded-md);
        }

        .chat-api-error {
          margin: 0.5rem;
          border-radius: var(--rounded-md);
        }

        @keyframes slideDown {
          from {
            transform: translateY(-10px);
            opacity: 0;
          }
          to {
            transform: translateY(0);
            opacity: 1;
          }
        }

        @media (max-width: 768px) {
          .app-content {
            flex-direction: column;
          }
          
          .editor-pane {
            max-width: 100%;
            height: 50vh;
            border-right: none;
            border-bottom: 1px solid var(--border-color);
          }
        }
      `}</style>
    </div>
  );
}

export default App;
