import React from 'react';
import { EditorPanel } from './editor/EditorPanel';
import { ChatPanel } from './chat/ChatPanel';
import { useChatContext } from '../contexts/ChatContext';
import '../styles/writing-workspace.css';

/**
 * WritingWorkspace - Clean layout component with single responsibility
 * 
 * RESPONSIBILITIES:
 * - Layout structure for editor + chat panels
 * - Responsive design handling
 * - Chat toggle UI
 * 
 * DOES NOT:
 * - Manage state (delegates to contexts)
 * - Handle business logic (delegates to child components)
 * - Duplicate context state
 */
export const WritingWorkspace: React.FC = () => {
  // Get chat visibility from ChatContext - single source of truth
  const { isChatVisible, toggleChat } = useChatContext();

  return (
    <div className="writing-workspace">
      {/* Main Writing Interface */}
      <div className={`workspace-layout ${isChatVisible ? 'with-chat' : 'editor-only'}`}>
        
        {/* Editor Panel - Always visible */}
        <div className="workspace-editor">
          <EditorPanel />
        </div>

        {/* Chat Panel - Conditionally visible */}
        {isChatVisible && (
          <div className="workspace-chat">
            <ChatPanel />
          </div>
        )}
      </div>

      {/* Chat Toggle Button - Clean separation */}
      <ChatToggleButton 
        isActive={isChatVisible}
        onToggle={toggleChat}
      />
    </div>
  );
};

/**
 * ChatToggleButton - Single responsibility component
 */
interface ChatToggleButtonProps {
  isActive: boolean;
  onToggle: () => void;
}

const ChatToggleButton: React.FC<ChatToggleButtonProps> = ({ isActive, onToggle }) => (
  <button 
    className={`chat-toggle-button ${isActive ? 'active' : ''}`}
    onClick={onToggle}
    title={isActive ? 'Close AI Chat' : 'Open AI Chat'}
    aria-label={isActive ? 'Close AI Chat' : 'Open AI Chat'}
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
  </button>
);

export default WritingWorkspace; 