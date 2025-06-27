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

// NEW: AI Interaction Modes - Similar to Cursor's Ask vs Agent
const AI_MODES = [
  {
    value: 'talk',
    label: 'Talk',
    icon: '💬',
    description: 'Conversational brainstorming and discussion'
  },
  {
    value: 'co-edit',
    label: 'Co-Edit',
    icon: '✏️',
    description: 'Direct text editing and improvement suggestions'
  }
];

interface ChatHeaderProps {
  authorPersona: string;
  helpFocus: string;
  selectedLLM: string;
  aiMode: string; // NEW: Add AI mode prop
  onAuthorPersonaChange: (persona: string) => void;
  onHelpFocusChange: (focus: string) => void;
  onLLMChange: (llm: string) => void;
  onAiModeChange: (mode: string) => void; // NEW: Add AI mode change handler
}

/**
 * Molecular Component: Chat Header
 * Single Responsibility: Display chat title and control selectors
 * 
 * ENHANCED: Now includes AI interaction mode selector (Talk vs Co-Edit)
 */
export const ChatHeader: React.FC<ChatHeaderProps> = ({
  authorPersona,
  helpFocus,
  selectedLLM,
  aiMode, // NEW
  onAuthorPersonaChange,
  onHelpFocusChange,
  onLLMChange,
  onAiModeChange // NEW
}) => {
  return (
    <div className="chat-header">
      <div className="chat-title">
        <span className="title-icon">💬</span>
        AI Writing Assistant
        <UnhighlightButton className="unhighlight-in-header" />
      </div>
      
      <div className="chat-controls-simple">
        {/* NEW: AI Mode Selector - Primary control, placed first */}
        <div className="control-select-group">
          <label title="AI Interaction Mode">🎯</label>
          <select 
            value={aiMode} 
            onChange={(e) => onAiModeChange(e.target.value)}
            className="control-select ai-mode-select"
            aria-label="Select AI interaction mode"
          >
            {AI_MODES.map((mode) => (
              <option 
                key={mode.value} 
                value={mode.value}
                title={mode.description}
              >
                {mode.icon} {mode.label}
              </option>
            ))}
          </select>
        </div>

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
          <label>📝</label>
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
 