/**
 * Writer's Desk Page
 * 
 * The main writing interface combining editor and chat in a clean,
 * minimalist layout with proper visual hierarchy.
 */

import React, { useRef } from 'react';
import { useAppContext } from '../contexts/AppContext';
import Editor from '../components/Editor';
import ChatPane from '../components/ChatPane';
import Controls from '../components/Controls';

const WritersDesk: React.FC = () => {
  const {
    editorContent,
    setEditorContent,
    handleTextHighlighted,
    chatApiError,
    apiGlobalError
  } = useAppContext();

  const editorRef = useRef<HTMLDivElement>(null);

  return (
    <div className="writers-desk">
      {/* Controls Section */}
      <div className="controls-section">
        <Controls />
      </div>

      {/* Error Messages */}
      {(apiGlobalError || chatApiError) && (
        <div className="error-alerts">
          {apiGlobalError && (
            <div className="alert alert-error">
              <svg className="alert-icon" xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <circle cx="12" cy="12" r="10"></circle>
                <line x1="15" y1="9" x2="9" y2="15"></line>
                <line x1="9" y1="9" x2="15" y2="15"></line>
              </svg>
              {apiGlobalError}
            </div>
          )}
          {chatApiError && (
            <div className="alert alert-warning">
              <svg className="alert-icon" xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3Z"></path>
                <line x1="12" y1="9" x2="12" y2="13"></line>
                <line x1="12" y1="17" x2="12.01" y2="17"></line>
              </svg>
              {chatApiError}
            </div>
          )}
        </div>
      )}

      {/* Main Writing Interface */}
      <div className="writing-interface">
        {/* Editor Panel - Text content at the top */}
        <div className="editor-panel">
          <div className="editor-container">
            <Editor 
              ref={editorRef}
              content={editorContent} 
              onChange={setEditorContent}
              onTextHighlighted={handleTextHighlighted}
            />
          </div>
        </div>

        {/* Chat Panel */}
        <div className="chat-panel">
          <ChatPane />
        </div>
      </div>
    </div>
  );
};

export default WritersDesk; 