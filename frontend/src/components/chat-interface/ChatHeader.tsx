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
  folderScopeEnabled: boolean; // Premium Feature 1
  voiceGuardEnabled: boolean; // Premium Feature 2
  onAuthorPersonaChange: (persona: string) => void;
  onHelpFocusChange: (focus: string) => void;
  onLLMChange: (llm: string) => void;
  onAiModeChange: (mode: string) => void; // NEW: Add AI mode change handler
  onFolderScopeChange: (enabled: boolean) => void; // Premium Feature 1 handler
  onVoiceGuardChange: (enabled: boolean) => void; // Premium Feature 2 handler
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
  folderScopeEnabled, // Premium Feature 1
  voiceGuardEnabled, // Premium Feature 2
  onAuthorPersonaChange,
  onHelpFocusChange,
  onLLMChange,
  onAiModeChange, // NEW
  onFolderScopeChange, // Premium Feature 1 handler
  onVoiceGuardChange // Premium Feature 2 handler
}) => {
  return (
    <>
      <style>{`
        .premium-features-group {
          display: flex;
          gap: 12px;
          align-items: center;
          padding: 4px 0;
          border-left: 2px solid var(--primary-500);
          padding-left: 12px;
          margin-left: 8px;
        }

        .premium-toggle {
          display: flex;
          align-items: center;
        }

        .toggle-label {
          display: flex;
          align-items: center;
          gap: 6px;
          cursor: pointer;
          font-size: 0.8125rem;
          font-weight: 500;
          color: var(--text-primary);
          transition: all 0.2s ease;
        }

        .toggle-label:hover {
          color: var(--primary-600);
        }

        .toggle-input {
          display: none;
        }

        .toggle-slider {
          position: relative;
          width: 32px;
          height: 16px;
          background: #9ca3af; /* Darker gray for better contrast */
          border: 1px solid #6b7280; /* Add border for definition */
          border-radius: 16px;
          transition: all 0.2s ease;
          flex-shrink: 0;
        }

        .toggle-slider::before {
          content: '';
          position: absolute;
          top: 2px;
          left: 2px;
          width: 12px;
          height: 12px;
          background: white;
          border-radius: 50%;
          transition: all 0.2s ease;
          box-shadow: 0 1px 3px rgba(0, 0, 0, 0.3); /* Slightly stronger shadow */
        }

        .toggle-input:checked + .toggle-slider {
          background: #3b82f6; /* More vibrant blue */
          border-color: #2563eb; /* Darker border for checked state */
        }

        .toggle-input:checked + .toggle-slider::before {
          transform: translateX(16px);
        }

        .toggle-text {
          font-size: 0.75rem;
          font-weight: 600;
          white-space: nowrap;
        }

        @media (max-width: 768px) {
          .premium-features-group {
            gap: 8px;
            margin-left: 4px;
            padding-left: 8px;
          }
          
          .toggle-text {
            font-size: 0.7rem;
          }
          
          .toggle-slider {
            width: 28px;
            height: 14px;
            background: #9ca3af; /* Maintain contrast on mobile */
            border: 1px solid #6b7280; /* Maintain border on mobile */
          }
          
          .toggle-slider::before {
            width: 10px;
            height: 10px;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.3); /* Maintain shadow on mobile */
          }
          
          .toggle-input:checked + .toggle-slider {
            background: #3b82f6; /* Maintain vibrant blue on mobile */
            border-color: #2563eb; /* Maintain border color on mobile */
          }
          
          .toggle-input:checked + .toggle-slider::before {
            transform: translateX(14px);
          }
        }
      `}</style>
      
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

          {/* Premium Features Toggles */}
          <div className="premium-features-group">
            <div className="premium-toggle">
              <label className="toggle-label">
                <input
                  type="checkbox"
                  checked={folderScopeEnabled}
                  onChange={(e) => onFolderScopeChange(e.target.checked)}
                  className="toggle-input"
                />
                <span className="toggle-slider"></span>
                <span className="toggle-text" title="Analyze all documents in current folder for deeper feedback">
                  📁 FolderScope⁺
                </span>
              </label>
            </div>
            
            <div className="premium-toggle">
              <label className="toggle-label">
                <input
                  type="checkbox"
                  checked={voiceGuardEnabled}
                  onChange={(e) => onVoiceGuardChange(e.target.checked)}
                  className="toggle-input"
                />
                <span className="toggle-slider"></span>
                <span className="toggle-text" title="Highlight inconsistent character voice in this draft">
                  🛡️ VoiceGuard
                </span>
              </label>
            </div>
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
    </>
  );
}; 
 