import React, { useState } from 'react';
import api, { MangaPageFE, MangaScriptResponseFE } from '../services/api';
import MangaDisplay from '../components/MangaDisplay';
import '../App.css'; // Assuming some shared styles might be in App.css or a global one
import { useAppContext } from '../contexts/AppContext';
import { logger } from '../utils/logger';

const MangaStudioPage: React.FC = () => {
  const { editorContent, authorPersona } = useAppContext();
  
  const [mangaPageData, setMangaPageData] = useState<MangaPageFE | null>(null);
  const [isGeneratingManga, setIsGeneratingManga] = useState(false);
  const [mangaError, setMangaError] = useState<string | null>(null);
  const [storyText, setStoryText] = useState<string>('');
  const [useEditorText, setUseEditorText] = useState<boolean>(true);

  const handleLoadFromEditor = () => {
    setStoryText(editorContent);
    setUseEditorText(false);
  };

  const handleGenerateManga = async () => {
    // Determine which text to use - either from editor (via context) or the local text input
    const textToUse = useEditorText ? editorContent : storyText;
    
    if (!textToUse.trim()) {
      setMangaError("Please provide some story text first, either from the editor or by typing it here.");
      return;
    }
    setIsGeneratingManga(true);
    setMangaError(null);
    setMangaPageData(null);
    try {
      const response: MangaScriptResponseFE = await api.generateMangaScript({
        story_text: textToUse,
        author_persona: authorPersona
      });
      if (response.error) {
        setMangaError(response.error);
        setMangaPageData(null);
      } else if (response.manga_page) {
        setMangaPageData(response.manga_page);
      } else {
        setMangaError("Received an unexpected response from the manga generator.");
      }
    } catch (error: any) { // Use any for error type in catch for now
      logger.error('Error generating manga:', error);
      if (error.response && error.response.data) {
        const errorDetail = error.response.data.error || error.response.data.detail || JSON.stringify(error.response.data);
        setMangaError(`API error generating manga: ${error.response.status} - ${errorDetail}`);
      } else if (error.response) {
        setMangaError(`API error generating manga: ${error.response.status} - ${error.response.statusText}`);
      } else {
        setMangaError(`Error generating manga: ${error.message}`);
      }
    }
    setIsGeneratingManga(false);
  };

  return (
    // Using app-content class for the same side-by-side layout as Writer's Desk
    <main className="app-content">
      {/* Left side - Input panel */}
      <div className="manga-input-pane">
        <div className="manga-input-options">
          <label>
            <input 
              type="radio" 
              checked={useEditorText} 
              onChange={() => setUseEditorText(true)} 
            />
            Use text from Writer's Desk
          </label>
          <label>
            <input 
              type="radio" 
              checked={!useEditorText} 
              onChange={() => setUseEditorText(false)} 
            />
            Enter text below
          </label>
          <button 
            onClick={handleLoadFromEditor} 
            className="load-editor-text-button"
            disabled={!editorContent.trim()}
          >
            Load Text from Editor
          </button>
        </div>

        {!useEditorText && (
          <textarea
            className="manga-text-input"
            value={storyText}
            onChange={(e) => setStoryText(e.target.value)}
            placeholder="Enter your story text here..."
            rows={10}
          />
        )}

        {useEditorText && (
          <div className="editor-preview">
            <h3>Text from Writer's Desk:</h3>
            <div className="editor-text-preview">
              {editorContent || "(No text available in editor)"}
            </div>
          </div>
        )}

        <button 
          onClick={handleGenerateManga} 
          disabled={isGeneratingManga || (useEditorText && !editorContent.trim()) || (!useEditorText && !storyText.trim())} 
          className="manga-generate-button"
        >
          {isGeneratingManga ? 'Generating Manga Page...' : 'Generate Manga'}
        </button>

      {mangaError && (
          <div className="manga-error-banner">
          <p>Manga Generation Error: {mangaError}</p>
        </div>
      )}
      </div>

      {/* Right side - Output display */}
      <div className="manga-display-pane">
      {isGeneratingManga && (
        <div className="manga-loading-placeholder">Generating your manga page... This can take up to a minute.</div>
      )}

      {mangaPageData && !isGeneratingManga && (
        <MangaDisplay mangaPage={mangaPageData} />
      )}
      
      {!mangaPageData && !isGeneratingManga && !mangaError && (
         <div className="manga-placeholder">
            <p>Your generated manga page will appear here.</p>
        </div>
      )}
      </div>

      <style>{`
        .manga-input-pane, .manga-display-pane {
          flex: 1;
          overflow: auto;
          padding: 20px;
          background-color: white;
          border-radius: 8px;
          box-shadow: 0 1px 3px rgba(0,0,0,0.1);
          display: flex;
          flex-direction: column;
        }
        
        .manga-input-pane {
          min-width: 0;
        }
        
        .manga-display-pane {
          min-width: 0;
        }
        
        .manga-input-options {
          display: flex;
          flex-wrap: wrap;
          align-items: center; 
          gap: 20px;
          margin-bottom: 15px;
        }
        
        .manga-text-input {
          width: 100%;
          padding: 12px;
          border: 1px solid #d1d5db;
          border-radius: 6px;
          font-family: inherit;
          margin-bottom: 15px;
          resize: vertical;
        }
        
        .manga-generate-button {
          padding: 10px 20px;
          font-size: 1em;
          cursor: pointer;
          background-color: #6366f1;
          color: white;
          border: none;
          border-radius: 8px;
          transition: background-color 0.2s;
          width: 100%;
        }
        
        .manga-generate-button:hover {
          background-color: #4f46e5;
        }
        
        .manga-generate-button:disabled {
          background-color: #a5b4fc;
          cursor: not-allowed;
        }
        
        .load-editor-text-button {
          padding: 6px 12px;
          font-size: 0.9em;
          background-color: #e5e7eb;
          border: none;
          border-radius: 4px;
          cursor: pointer;
        }
        
        .load-editor-text-button:hover {
          background-color: #d1d5db;
        }
        
        .load-editor-text-button:disabled {
          opacity: 0.5;
          cursor: not-allowed;
        }
        
        .editor-preview {
          background-color: #f9fafb;
          border: 1px solid #e5e7eb;
          border-radius: 6px;
          padding: 15px;
          margin-bottom: 15px;
        }
        
        .editor-preview h3 {
          margin-top: 0;
          font-size: 1em;
          color: #4b5563;
          margin-bottom: 10px;
        }
        
        .editor-text-preview {
          max-height: 200px;
          overflow-y: auto;
          white-space: pre-wrap;
          font-size: 0.95em;
        }
        
        .manga-error-banner {
          background-color: #fee2e2;
          color: #b91c1c;
          padding: 10px;
          margin: 15px 0;
          text-align: center;
          border: 1px solid #fecaca;
          border-radius: 4px;
        }
        
        .manga-loading-placeholder, .manga-placeholder {
            text-align: center;
            font-size: 1.2em;
            color: #555;
          margin-top: 30px;
          display: flex;
          justify-content: center;
          align-items: center;
          height: 100%;
        }
        
        @media (max-width: 768px) {
          .manga-input-pane, .manga-display-pane {
            height: auto;
            flex: none;
            margin-bottom: 20px;
          }
        }
      `}</style>
    </main>
  );
};

export default MangaStudioPage; 