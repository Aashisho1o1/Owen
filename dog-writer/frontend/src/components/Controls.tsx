import React from 'react';
import { useAppContext } from '../contexts/AppContext';

const Controls: React.FC = () => {
  const {
    authorPersona,
    helpFocus,
    selectedLLM,
    setAuthorPersona,
    setHelpFocus,
    setSelectedLLM,
    handleSaveCheckpoint
  } = useAppContext();

  const authors = [
    "Ernest Hemingway",
    "Jane Austen",
    "Virginia Woolf"
  ];

  const helpFocuses = [
    "Dialogue Writing",
    "Scene Description",
    "Plot Development",
    "Character Introduction",
    "Overall Tone"
  ];

  const llmOptions = [
    "Google Gemini",
    "Anthropic Claude"
  ];

  return (
    <div className="controls-container">
      <div className="controls-group">
        <label htmlFor="author-select">Author Persona</label>
        <select
          id="author-select"
          value={authorPersona}
          onChange={(e) => setAuthorPersona(e.target.value)}
          className="select-control"
        >
          {authors.map(author => (
            <option key={author} value={author}>{author}</option>
          ))}
        </select>
      </div>

      <div className="controls-group">
        <label htmlFor="focus-select">Help Focus</label>
        <select
          id="focus-select"
          value={helpFocus}
          onChange={(e) => setHelpFocus(e.target.value)}
          className="select-control"
        >
          {helpFocuses.map(focus => (
            <option key={focus} value={focus}>{focus}</option>
          ))}
        </select>
      </div>

      <div className="controls-group">
        <label htmlFor="llm-select">AI Model</label>
        <select
          id="llm-select"
          value={selectedLLM}
          onChange={(e) => setSelectedLLM(e.target.value)}
          className="select-control"
        >
          {llmOptions.map(llm => (
            <option key={llm} value={llm}>{llm}</option>
          ))}
        </select>
      </div>

      <button 
        className="checkpoint-button"
        onClick={handleSaveCheckpoint}
      >
        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <path d="M19 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11l5 5v11a2 2 0 0 1-2 2z"></path>
          <polyline points="17 21 17 13 7 13 7 21"></polyline>
          <polyline points="7 3 7 8 15 8"></polyline>
        </svg>
        Save Checkpoint
      </button>

      <style>{`
        .controls-container {
          display: flex;
          align-items: center;
          padding: 12px 24px;
          background-color: white;
          border-bottom: 1px solid #e2e8f0;
          gap: 20px;
          box-shadow: var(--shadow-sm);
          z-index: 5;
        }
        
        .controls-group {
          display: flex;
          flex-direction: column;
          gap: 6px;
        }
        
        label {
          font-weight: 500;
          color: var(--text-secondary);
          font-size: 0.875rem;
        }
        
        .select-control {
          padding: 8px 12px;
          border: 1px solid #e2e8f0;
          border-radius: var(--rounded-md);
          font-size: 0.875rem;
          min-width: 200px;
          background-color: #f8fafc;
          color: var(--text-primary);
          transition: all 0.2s;
          outline: none;
          box-shadow: var(--shadow-sm);
        }
        
        .select-control:focus {
          border-color: var(--primary-light);
          box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.15);
        }
        
        .checkpoint-button {
          display: flex;
          align-items: center;
          gap: 8px;
          padding: 8px 16px;
          background-color: var(--accent-color);
          color: white;
          border: none;
          border-radius: var(--rounded-md);
          cursor: pointer;
          margin-left: auto;
          font-weight: 500;
          transition: all 0.2s;
          box-shadow: var(--shadow-sm);
        }
        
        .checkpoint-button:hover {
          background-color: #0d9488;
          transform: translateY(-1px);
          box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
        }
        
        .checkpoint-button:active {
          transform: translateY(0);
        }
        
        @media (max-width: 768px) {
          .controls-container {
            flex-wrap: wrap;
            gap: 16px;
            padding: 12px 16px;
          }
          
          .checkpoint-button {
            margin-left: 0;
            width: 100%;
            justify-content: center;
          }
        }
      `}</style>
    </div>
  );
};

export default Controls; 