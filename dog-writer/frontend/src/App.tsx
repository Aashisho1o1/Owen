import React from 'react';
import { Routes, Route, Link, Outlet, useLocation } from 'react-router-dom';
import Editor from './components/Editor';
import ChatPane from './components/ChatPane';
import Controls from './components/Controls';
import MangaStudioPage from './pages/MangaStudioPage';
import SoundToSpeechPage from './pages/SoundToSpeechPage';
import './App.css';
import { useAppContext } from './contexts/AppContext';

// Main layout component that includes header and controls
const AppLayout: React.FC = () => {
  const { 
    apiGlobalError 
  } = useAppContext();
  
  const location = useLocation();
  const isFullscreenRoute = location.pathname === '/sound-to-speech';

  return (
    <>
      <header className="app-header" style={{
        display: isFullscreenRoute ? 'none' : 'flex'
      }}>
        <h1>Owen</h1>
        <nav className="app-nav">
          <Link to="/">Writer's Desk</Link>
          <Link to="/manga">Manga Studio</Link>
          <Link to="/sound-to-speech">Sound to Speech</Link>
        </nav>
      </header>
      {!isFullscreenRoute && <Controls />}
      {apiGlobalError && (
        <div className="api-error-banner global-api-error">
          <p>{apiGlobalError}</p>
        </div>
      )}
      <div className={`layout-container ${isFullscreenRoute ? 'layout-container--fullscreen' : 'layout-container--with-header'}`}>
        <Outlet />
      </div>
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
          <Route path="sound-to-speech" element={<SoundToSpeechPage />} />
        </Route>
      </Routes>
    </div>
  );
}

export default App;
