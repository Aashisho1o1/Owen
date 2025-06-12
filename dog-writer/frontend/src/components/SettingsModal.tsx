import React from 'react';
import { useTheme } from '../contexts/ThemeContext';

interface SettingsModalProps {
  isOpen: boolean;
  onClose: () => void;
}

const SettingsModal: React.FC<SettingsModalProps> = ({ isOpen, onClose }) => {
  const { theme, toggleTheme } = useTheme();

  if (!isOpen) return null;

  const handleBackdropClick = (e: React.MouseEvent) => {
    if (e.target === e.currentTarget) {
      onClose();
    }
  };

  return (
    <div className="settings-modal-backdrop" onClick={handleBackdropClick}>
      <div className="settings-modal">
        <div className="settings-header">
          <h2>Settings</h2>
          <button className="close-button" onClick={onClose}>
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <line x1="18" y1="6" x2="6" y2="18"></line>
              <line x1="6" y1="6" x2="18" y2="18"></line>
            </svg>
          </button>
        </div>

        <div className="settings-content">
          <div className="settings-section">
            <h3>Appearance</h3>
            
            <div className="setting-item">
              <div className="setting-info">
                <label>Theme</label>
                <p>Choose your preferred color scheme</p>
              </div>
              
              <div className="theme-toggle">
                <button 
                  className={`theme-option ${theme === 'light' ? 'active' : ''}`}
                  onClick={() => theme !== 'light' && toggleTheme()}
                >
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <circle cx="12" cy="12" r="5"/>
                    <line x1="12" y1="1" x2="12" y2="3"/>
                    <line x1="12" y1="21" x2="12" y2="23"/>
                    <line x1="4.22" y1="4.22" x2="5.64" y2="5.64"/>
                    <line x1="18.36" y1="18.36" x2="19.78" y2="19.78"/>
                    <line x1="1" y1="12" x2="3" y2="12"/>
                    <line x1="21" y1="12" x2="23" y2="12"/>
                    <line x1="4.22" y1="19.78" x2="5.64" y2="18.36"/>
                    <line x1="18.36" y1="5.64" x2="19.78" y2="4.22"/>
                  </svg>
                  Light
                </button>
                
                <button 
                  className={`theme-option ${theme === 'dark' ? 'active' : ''}`}
                  onClick={() => theme !== 'dark' && toggleTheme()}
                >
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/>
                  </svg>
                  Dark
                </button>
              </div>
            </div>
          </div>
          
          <div className="settings-section">
            <h3>About</h3>
            <div className="setting-item">
              <div className="setting-info">
                <label>Owen AI Writing Assistant</label>
                <p>Version 2.0.0 - Your intelligent writing companion</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <style>{`
        .settings-modal-backdrop {
          position: fixed;
          top: 0;
          left: 0;
          right: 0;
          bottom: 0;
          background: rgba(0, 0, 0, 0.5);
          backdrop-filter: blur(4px);
          display: flex;
          align-items: center;
          justify-content: center;
          z-index: 1000;
          animation: fadeIn 0.2s ease-out;
        }

        @keyframes fadeIn {
          from { opacity: 0; }
          to { opacity: 1; }
        }

        .settings-modal {
          background: var(--bg-primary);
          border-radius: 12px;
          box-shadow: var(--shadow-lg);
          width: 100%;
          max-width: 500px;
          max-height: 80vh;
          overflow: hidden;
          animation: slideIn 0.3s ease-out;
          border: 1px solid var(--border-primary);
        }

        @keyframes slideIn {
          from { 
            opacity: 0;
            transform: translateY(-20px) scale(0.95);
          }
          to { 
            opacity: 1;
            transform: translateY(0) scale(1);
          }
        }

        .settings-header {
          display: flex;
          align-items: center;
          justify-content: between;
          padding: 24px;
          border-bottom: 1px solid var(--border-primary);
        }

        .settings-header h2 {
          margin: 0;
          font-size: 1.5rem;
          font-weight: 600;
          color: var(--text-primary);
          flex: 1;
        }

        .close-button {
          background: none;
          border: none;
          color: var(--text-muted);
          cursor: pointer;
          padding: 8px;
          border-radius: 6px;
          transition: all 0.2s;
        }

        .close-button:hover {
          background: var(--bg-hover);
          color: var(--text-primary);
        }

        .settings-content {
          padding: 24px;
          max-height: 60vh;
          overflow-y: auto;
        }

        .settings-section {
          margin-bottom: 32px;
        }

        .settings-section:last-child {
          margin-bottom: 0;
        }

        .settings-section h3 {
          margin: 0 0 16px 0;
          font-size: 1.125rem;
          font-weight: 600;
          color: var(--text-primary);
        }

        .setting-item {
          display: flex;
          align-items: center;
          justify-content: between;
          padding: 16px 0;
        }

        .setting-info {
          flex: 1;
        }

        .setting-info label {
          display: block;
          font-size: 1rem;
          font-weight: 500;
          color: var(--text-primary);
          margin-bottom: 4px;
        }

        .setting-info p {
          margin: 0;
          font-size: 0.875rem;
          color: var(--text-muted);
        }

        .theme-toggle {
          display: flex;
          background: var(--bg-secondary);
          border-radius: 8px;
          padding: 4px;
          gap: 4px;
          border: 1px solid var(--border-primary);
        }

        .theme-option {
          display: flex;
          align-items: center;
          gap: 8px;
          padding: 8px 16px;
          background: none;
          border: none;
          border-radius: 6px;
          cursor: pointer;
          font-size: 0.875rem;
          font-weight: 500;
          color: var(--text-secondary);
          transition: all 0.2s;
        }

        .theme-option:hover {
          background: var(--bg-hover);
          color: var(--text-primary);
        }

        .theme-option.active {
          background: var(--accent-blue);
          color: white;
        }

        .theme-option.active:hover {
          background: var(--accent-blue-hover);
        }

        .theme-option svg {
          width: 16px;
          height: 16px;
        }
      `}</style>
    </div>
  );
};

export default SettingsModal; 