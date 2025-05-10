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

import React, { useState } from 'react';
import { Routes, Route, Link, Outlet } from 'react-router-dom';
import Editor from './components/Editor';
import ChatPane from './components/ChatPane';
import Controls from './components/Controls';
import api, { ChatMessage } from './services/api';
import MangaStudioPage from './pages/MangaStudioPage';
import VoiceNotesPage from './pages/VoiceNotesPage';
import './App.css';
import { useChat } from './hooks/useChat';
import { useEditor } from './hooks/useEditor';
import { useApiHealth } from './hooks/useApiHealth';

// Type for API errors from AxiosError-like objects
interface ApiErrorData {
  error?: string; // Common pattern for FastAPI validation errors or custom errors
  detail?: string | Array<{ loc: string[]; msg: string; type: string }>; // FastAPI validation errors often have detail
  // Allow other string-keyed properties
  [key: string]: unknown;
}

interface ApiError {
  message: string;
  response?: {
    status: number;
    statusText: string;
    data?: ApiErrorData; // More specific type for error data
  };
  request?: unknown; // Use unknown for request as its structure is complex and not directly used for error messages here
}

// Main layout component that includes header and controls
const AppLayout: React.FC<{ 
  authorPersona: string; 
  helpFocus: string; 
  selectedLLM: string;
  onAuthorChange: (val: string) => void;
  onHelpFocusChange: (val: string) => void;
  onLLMChange: (val: string) => void;
  onSaveCheckpoint: () => void;
  apiGlobalError: string | null;
}> = ({ authorPersona, helpFocus, selectedLLM, onAuthorChange, onHelpFocusChange, onLLMChange, onSaveCheckpoint, apiGlobalError }) => {
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
      <Controls
        authorPersona={authorPersona}
        helpFocus={helpFocus}
        selectedLLM={selectedLLM}
        onAuthorChange={onAuthorChange}
        onHelpFocusChange={onHelpFocusChange}
        onLLMChange={onLLMChange}
        onSaveCheckpoint={onSaveCheckpoint}
      />
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
const WritersDesk: React.FC<{
  editorContent: string;
  setEditorContent: (content: string) => void;
  handleTextHighlighted: (text: string) => void;
  messages: ChatMessage[];
  handleSendMessage: (message: string) => Promise<void>;
  thinkingTrail: string | null;
  highlightedText: string | null;
  helpFocus: string;
  authorPersona: string;
  isStreaming: boolean;
  streamingText: string;
  isThinking: boolean;
  chatApiError: string | null;
}> = (props) => {
  return (
    <main className="app-content">
      <div className="editor-pane">
        <Editor 
          content={props.editorContent} 
          onChange={props.setEditorContent}
          onTextHighlighted={props.handleTextHighlighted}
        />
      </div>
      <div className="chat-and-manga-pane">
        {props.chatApiError && (
          <div className="api-error-banner chat-api-error">
            <p>{props.chatApiError}</p>
          </div>
        )}
        <ChatPane 
          messages={props.messages} 
          onSendMessage={props.handleSendMessage}
          thinkingTrail={props.thinkingTrail}
          highlightedText={props.highlightedText}
          helpFocus={props.helpFocus}
          authorPersona={props.authorPersona}
          isStreaming={props.isStreaming}
          streamingText={props.streamingText}
          isThinking={props.isThinking}
        />
      </div>
    </main>
  );
};

function App() {
  const [authorPersona, setAuthorPersona] = useState('Ernest Hemingway');
  const [helpFocus, setHelpFocus] = useState('Dialogue Writing');
  const [selectedLLM, setSelectedLLM] = useState('Google Gemini');

  const { apiGlobalError, setApiGlobalError, checkApiConnection, clearApiGlobalError } = useApiHealth();

  const {
    editorContent,
    setEditorContent,
    highlightedText,
    handleTextHighlighted,
  } = useEditor({});

  const {
    messages,
    thinkingTrail,
    apiError: chatApiError,
    isStreaming,
    streamText,
    isThinking,
    handleSendMessage,
  } = useChat({
    authorPersona,
    helpFocus,
    editorContent,
    selectedLLM,
  });

  const handleSaveCheckpoint = async () => {
    console.log("Save Checkpoint clicked");
    try {
      await api.createCheckpoint({ editor_text: editorContent, chat_history: messages });
      console.log("Checkpoint saved successfully.");
    } catch (error) {
      const typedError = error as ApiError;
      let specificApiError = `Error saving checkpoint: ${typedError.message || 'Unknown error'}`;
      if (typedError.response && typedError.response.data) {
        const errorDetail = typedError.response.data.detail || typedError.response.data.error || JSON.stringify(typedError.response.data);
        specificApiError = `Checkpoint API error: ${typedError.response.status} - ${errorDetail}`;
      } else if (typedError.response) {
        specificApiError = `Checkpoint API error: ${typedError.response.status} - ${typedError.response.statusText}`;
      }
      setApiGlobalError(specificApiError);
    }
  };

  return (
    <div className="app">
      <Routes>
        <Route 
          path="/" 
          element={(
            <AppLayout 
              authorPersona={authorPersona} 
              helpFocus={helpFocus} 
              selectedLLM={selectedLLM} 
              onAuthorChange={setAuthorPersona} 
              onHelpFocusChange={setHelpFocus} 
              onLLMChange={setSelectedLLM}
              onSaveCheckpoint={handleSaveCheckpoint}
              apiGlobalError={apiGlobalError}
            />
          )}
        >
          <Route 
            index 
            element={(
              <WritersDesk 
                editorContent={editorContent}
                setEditorContent={setEditorContent}
                handleTextHighlighted={handleTextHighlighted}
                messages={messages}
                handleSendMessage={handleSendMessage}
                thinkingTrail={thinkingTrail}
                highlightedText={highlightedText}
                helpFocus={helpFocus}
                authorPersona={authorPersona}
                isStreaming={isStreaming}
                streamingText={streamText}
                isThinking={isThinking}
                chatApiError={chatApiError}
              />
            )} 
          />
          <Route 
            path="manga" 
            element={(
              <MangaStudioPage 
                editorStoryText={editorContent} 
                currentAuthorPersona={authorPersona} 
              />
            )} 
          />
          <Route 
            path="voice-notes" 
            element={<VoiceNotesPage />} 
          />
        </Route>
      </Routes>
      
      <style>{`
        .app-nav {
          margin-left: auto;
          display: flex;
          gap: 1rem;
        }
        .app-nav a {
          color: white;
          text-decoration: none;
          padding: 0.5rem 1rem;
          border-radius: 4px;
          transition: background-color 0.2s;
        }
        .app-nav a:hover, .app-nav a.active {
          background-color: rgba(255,255,255,0.2);
        }
        .api-error-banner {
          background-color: #fee2e2;
          color: #b91c1c;
          padding: 10px;
          margin: 0;
          text-align: center;
          border: 1px solid #fecaca;
          position: fixed;
          bottom: 0;
          left: 0;
          width: 100%;
          z-index: 1000;
        }
        .app {
          display: flex;
          flex-direction: column;
          height: 100vh;
          overflow: hidden;
        }
        .app-content {
          flex: 1;
          overflow: hidden;
          padding: 1.5rem;
          gap: 1.5rem;
          display: flex;
        }
        .editor-pane, .chat-and-manga-pane {
          flex: 1;
          min-width: 0;
          display: flex;
          flex-direction: column;
          overflow: hidden;
          background-color: white;
        }
        .chat-pane .messages-container {
          background-color: white !important;
        }
        .chat-pane .chat-container {
          background-color: white !important;
        }
        @media (max-width: 768px) {
          .app-content {
            flex-direction: column;
            overflow-y: auto;
          }
          .editor-pane, .chat-and-manga-pane {
            height: auto;
            flex: 1;
            overflow: visible;
          }
        }
      `}</style>
    </div>
  );
}

export default App;
