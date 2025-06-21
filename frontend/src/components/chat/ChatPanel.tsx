import React from 'react';
import ChatPane from '../ChatPane';
import '../../styles/chat-panel.css';

/**
 * ChatPanel - Wrapper for chat functionality
 * 
 * SINGLE RESPONSIBILITY:
 * - Provide chat panel layout structure
 * - Delegate all chat logic to ChatPane
 * 
 * ARCHITECTURE BENEFIT:
 * - Clear separation between layout (ChatPanel) and logic (ChatPane)  
 * - Easy to swap chat implementations
 * - Consistent with editor panel structure
 */
export const ChatPanel: React.FC = () => {
  return (
    <div className="chat-panel-container">
      <ChatPane />
    </div>
  );
};

export default ChatPanel; 