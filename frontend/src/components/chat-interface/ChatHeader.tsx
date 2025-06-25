import React from 'react';
import { UnhighlightButton } from './UnhighlightButton';

// Constants
const AUTHOR_PERSONAS = [
  'Ernest Hemingway',
  'Virginia Woolf', 
  'Maya Angelou',
  'George Orwell',
  'Toni Morrison',
  'J.K. Rowling',
  'Haruki Murakami',
  'Margaret Atwood'
];

const HELP_FOCUSES = [
  'Dialogue Writing',
  'Scene Description', 
  'Plot Development',
  'Character Introduction',
  'Overall Tone'
];

const LLM_OPTIONS = [
  'OpenAI GPT',
  'Google Gemini',
];

interface ChatHeaderProps {
  authorPersona: string;
  helpFocus: string;
  selectedLLM: string;
  onAuthorPersonaChange: (persona: string) => void;
  onHelpFocusChange: (focus: string) => void;
  onLLMChange: (llm: string) => void;
}

/**
 * Molecular Component: Chat Header
 * Single Responsibility: Display chat title and control selectors
 */
export const ChatHeader: React.FC<ChatHeaderProps> = ({
  authorPersona,
  helpFocus,
  selectedLLM,
  onAuthorPersonaChange,
  onHelpFocusChange,
  onLLMChange
}) => {
  return (
    <div className="chat-header">
      <div className="chat-title">
        <span className="title-icon">💬</span>
        AI Writing Assistant
        <UnhighlightButton className="unhighlight-in-header" />
      </div>
      
      <div className="chat-controls-simple">
        <div className="control-select-group">
          <label>👤</label>
          <select 
            value={authorPersona} 
            onChange={(e) => onAuthorPersonaChange(e.target.value)}
            className="control-select"
            aria-label="Select author persona"
          >
            {AUTHOR_PERSONAS.map((persona) => (
              <option key={persona} value={persona}>
                {persona}
              </option>
            ))}
          </select>
        </div>
        
        <div className="control-select-group">
          <label>🎯</label>
          <select 
            value={helpFocus} 
            onChange={(e) => onHelpFocusChange(e.target.value)}
            className="control-select"
            aria-label="Select writing focus"
          >
            {HELP_FOCUSES.map((focus) => (
              <option key={focus} value={focus}>
                {focus}
              </option>
            ))}
          </select>
        </div>
        
        <div className="control-select-group">
          <label>🤖</label>
          <select 
            value={selectedLLM} 
            onChange={(e) => onLLMChange(e.target.value)}
            className="control-select"
            aria-label="Select AI model"
          >
            {LLM_OPTIONS.map((model) => (
              <option key={model} value={model}>
                {model}
              </option>
            ))}
          </select>
        </div>
      </div>
    </div>
  );
}; 
 