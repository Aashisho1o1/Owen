import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { useAppContext } from '../contexts/AppContext';

const DocumentHelp: React.FC = () => {
  const { isAuthenticated } = useAuth();
  const { documentManager } = useAppContext();
  const [showHelp, setShowHelp] = useState(false);
  const [dismissed, setDismissed] = useState(false);

  // Show help banner when user first uses the app or isn't authenticated
  useEffect(() => {
    const hasSeenHelp = localStorage.getItem('document-help-seen');
    if (!hasSeenHelp && !dismissed) {
      setShowHelp(true);
    }
  }, [dismissed]);

  const handleDismiss = () => {
    setShowHelp(false);
    setDismissed(true);
    localStorage.setItem('document-help-seen', 'true');
  };

  if (!showHelp || (isAuthenticated && documentManager.documents.length > 0)) {
    return null;
  }

  return (
    <div className="document-help-banner">
      <div className="help-content">
        <div className="help-icon">💡</div>
        <div className="help-text">
          {!isAuthenticated ? (
            <>
              <strong>Save Your Work:</strong> Sign in to automatically save your writing and access it from anywhere.
            </>
          ) : (
            <>
              <strong>Getting Started:</strong> Your writing auto-saves every 2 seconds. Click the 📄 Documents button to manage your files.
            </>
          )}
        </div>
      </div>
      <button 
        onClick={handleDismiss}
        className="help-dismiss"
        aria-label="Dismiss help"
      >
        ×
      </button>

      <style jsx>{`
        .document-help-banner {
          background: linear-gradient(135deg, #eff6ff 0%, #dbeafe 100%);
          border: 1px solid #bfdbfe;
          border-radius: 8px;
          padding: 12px 16px;
          margin: 8px 16px;
          display: flex;
          align-items: center;
          gap: 12px;
          font-size: 14px;
          color: #1e40af;
          box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
        }

        .help-content {
          display: flex;
          align-items: center;
          gap: 8px;
          flex: 1;
        }

        .help-icon {
          font-size: 16px;
          flex-shrink: 0;
        }

        .help-text {
          line-height: 1.4;
        }

        .help-text strong {
          font-weight: 600;
          color: #1d4ed8;
        }

        .help-dismiss {
          background: none;
          border: none;
          color: #6b7280;
          cursor: pointer;
          font-size: 20px;
          line-height: 1;
          padding: 4px;
          border-radius: 4px;
          transition: all 0.15s;
          flex-shrink: 0;
        }

        .help-dismiss:hover {
          background: rgba(59, 130, 246, 0.1);
          color: #374151;
        }

        @media (max-width: 768px) {
          .document-help-banner {
            margin: 6px 12px;
            padding: 10px 12px;
            font-size: 13px;
          }
        }
      `}</style>
    </div>
  );
};

export default DocumentHelp; 
import { useAuth } from '../contexts/AuthContext';
import { useAppContext } from '../contexts/AppContext';

const DocumentHelp: React.FC = () => {
  const { isAuthenticated } = useAuth();
  const { documentManager } = useAppContext();
  const [showHelp, setShowHelp] = useState(false);
  const [dismissed, setDismissed] = useState(false);

  // Show help banner when user first uses the app or isn't authenticated
  useEffect(() => {
    const hasSeenHelp = localStorage.getItem('document-help-seen');
    if (!hasSeenHelp && !dismissed) {
      setShowHelp(true);
    }
  }, [dismissed]);

  const handleDismiss = () => {
    setShowHelp(false);
    setDismissed(true);
    localStorage.setItem('document-help-seen', 'true');
  };

  if (!showHelp || (isAuthenticated && documentManager.documents.length > 0)) {
    return null;
  }

  return (
    <div className="document-help-banner">
      <div className="help-content">
        <div className="help-icon">💡</div>
        <div className="help-text">
          {!isAuthenticated ? (
            <>
              <strong>Save Your Work:</strong> Sign in to automatically save your writing and access it from anywhere.
            </>
          ) : (
            <>
              <strong>Getting Started:</strong> Your writing auto-saves every 2 seconds. Click the 📄 Documents button to manage your files.
            </>
          )}
        </div>
      </div>
      <button 
        onClick={handleDismiss}
        className="help-dismiss"
        aria-label="Dismiss help"
      >
        ×
      </button>

      <style jsx>{`
        .document-help-banner {
          background: linear-gradient(135deg, #eff6ff 0%, #dbeafe 100%);
          border: 1px solid #bfdbfe;
          border-radius: 8px;
          padding: 12px 16px;
          margin: 8px 16px;
          display: flex;
          align-items: center;
          gap: 12px;
          font-size: 14px;
          color: #1e40af;
          box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
        }

        .help-content {
          display: flex;
          align-items: center;
          gap: 8px;
          flex: 1;
        }

        .help-icon {
          font-size: 16px;
          flex-shrink: 0;
        }

        .help-text {
          line-height: 1.4;
        }

        .help-text strong {
          font-weight: 600;
          color: #1d4ed8;
        }

        .help-dismiss {
          background: none;
          border: none;
          color: #6b7280;
          cursor: pointer;
          font-size: 20px;
          line-height: 1;
          padding: 4px;
          border-radius: 4px;
          transition: all 0.15s;
          flex-shrink: 0;
        }

        .help-dismiss:hover {
          background: rgba(59, 130, 246, 0.1);
          color: #374151;
        }

        @media (max-width: 768px) {
          .document-help-banner {
            margin: 6px 12px;
            padding: 10px 12px;
            font-size: 13px;
          }
        }
      `}</style>
    </div>
  );
};

export default DocumentHelp; 