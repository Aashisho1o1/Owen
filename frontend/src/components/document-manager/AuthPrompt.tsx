import React from 'react';

interface AuthPromptProps {
  onClose: () => void;
}

/**
 * Molecular component: Auth Prompt
 * Single Responsibility: Display authentication required message
 */
export const AuthPrompt: React.FC<AuthPromptProps> = ({ onClose }) => {
  return (
    <div className="document-manager-overlay">
      <div className="document-manager">
        <div className="document-manager-header">
          <h2>📄 Document Manager</h2>
          <button onClick={onClose} className="close-button">✕</button>
        </div>
        <div className="auth-prompt">
          <div className="auth-prompt-content">
            <h3>🔐 Sign In Required</h3>
            <p>Please sign in to access your documents and writing projects.</p>
          </div>
        </div>
      </div>
    </div>
  );
}; 
 