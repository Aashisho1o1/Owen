import React, { useState, useRef, useEffect } from 'react';
import { useAppContext } from '../contexts/AppContext';
import { useAuth } from '../contexts/AuthContext';

const DocumentTitleBar: React.FC = () => {
  const { isAuthenticated } = useAuth();
  const { documentManager } = useAppContext();
  const [isEditing, setIsEditing] = useState(false);
  const [editTitle, setEditTitle] = useState('');
  const inputRef = useRef<HTMLInputElement>(null);

  const { currentDocument, hasUnsavedChanges, isSaving, setCurrentTitle } = documentManager;

  useEffect(() => {
    if (currentDocument) {
      setEditTitle(currentDocument.title);
    }
  }, [currentDocument]);

  useEffect(() => {
    if (isEditing && inputRef.current) {
      inputRef.current.focus();
      inputRef.current.select();
    }
  }, [isEditing]);

  const handleStartEdit = () => {
    if (!currentDocument) return;
    setIsEditing(true);
  };

  const handleSaveTitle = () => {
    if (!currentDocument || !editTitle.trim()) {
      setEditTitle(currentDocument?.title || '');
      setIsEditing(false);
      return;
    }

    if (editTitle.trim() !== currentDocument.title) {
      setCurrentTitle(editTitle.trim());
    }
    setIsEditing(false);
  };

  const handleCancelEdit = () => {
    setEditTitle(currentDocument?.title || '');
    setIsEditing(false);
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      handleSaveTitle();
    } else if (e.key === 'Escape') {
      handleCancelEdit();
    }
  };

  const getSaveStatus = () => {
    if (!isAuthenticated) return null;
    if (!currentDocument) return null;
    if (isSaving) return 'Saving...';
    if (hasUnsavedChanges) return 'Unsaved changes';
    return 'Saved';
  };

  const saveStatus = getSaveStatus();

  return (
    <div className="document-title-bar">
      <div className="title-section">
        {currentDocument ? (
          <>
            {isEditing ? (
              <input
                ref={inputRef}
                type="text"
                value={editTitle}
                onChange={(e) => setEditTitle(e.target.value)}
                onBlur={handleSaveTitle}
                onKeyDown={handleKeyDown}
                className="title-input"
                placeholder="Document title..."
              />
            ) : (
              <h1 
                className="document-title"
                onClick={handleStartEdit}
                title="Click to edit title"
              >
                {currentDocument.title}
              </h1>
            )}
          </>
        ) : (
          <h1 className="document-title untitled">
            Untitled Document
          </h1>
        )}
      </div>

      {saveStatus && (
        <div className={`save-status ${isSaving ? 'saving' : hasUnsavedChanges ? 'unsaved' : 'saved'}`}>
          <span className="status-indicator">
            {isSaving ? '⏳' : hasUnsavedChanges ? '●' : '✓'}
          </span>
          <span className="status-text">{saveStatus}</span>
        </div>
      )}

      <style jsx>{`
        .document-title-bar {
          display: flex;
          align-items: center;
          justify-content: space-between;
          padding: 8px 16px;
          background: #fafafa;
          border-bottom: 1px solid #e5e7eb;
          min-height: 48px;
        }

        .title-section {
          flex: 1;
          min-width: 0;
        }

        .document-title {
          margin: 0;
          font-size: 16px;
          font-weight: 500;
          color: #111827;
          cursor: text;
          padding: 4px 8px;
          border-radius: 4px;
          transition: background-color 0.15s;
          white-space: nowrap;
          overflow: hidden;
          text-overflow: ellipsis;
          max-width: 400px;
        }

        .document-title:hover {
          background: #f3f4f6;
        }

        .document-title.untitled {
          color: #6b7280;
          font-style: italic;
          cursor: default;
        }

        .document-title.untitled:hover {
          background: transparent;
        }

        .title-input {
          font-size: 16px;
          font-weight: 500;
          color: #111827;
          border: 2px solid #3b82f6;
          border-radius: 4px;
          padding: 4px 8px;
          background: white;
          outline: none;
          min-width: 200px;
          max-width: 400px;
        }

        .save-status {
          display: flex;
          align-items: center;
          gap: 4px;
          font-size: 12px;
          padding: 4px 8px;
          border-radius: 4px;
          white-space: nowrap;
        }

        .save-status.saving {
          color: #3b82f6;
          background: #eff6ff;
        }

        .save-status.unsaved {
          color: #f59e0b;
          background: #fffbeb;
        }

        .save-status.saved {
          color: #10b981;
          background: #ecfdf5;
        }

        .status-indicator {
          font-size: 10px;
          line-height: 1;
        }

        .status-text {
          font-weight: 500;
        }

        @media (max-width: 768px) {
          .document-title-bar {
            padding: 6px 12px;
          }

          .document-title,
          .title-input {
            font-size: 14px;
            max-width: 250px;
          }

          .save-status {
            font-size: 11px;
          }
        }
      `}</style>
    </div>
  );
};

export default DocumentTitleBar; 
import { useAppContext } from '../contexts/AppContext';
import { useAuth } from '../contexts/AuthContext';

const DocumentTitleBar: React.FC = () => {
  const { isAuthenticated } = useAuth();
  const { documentManager } = useAppContext();
  const [isEditing, setIsEditing] = useState(false);
  const [editTitle, setEditTitle] = useState('');
  const inputRef = useRef<HTMLInputElement>(null);

  const { currentDocument, hasUnsavedChanges, isSaving, setCurrentTitle } = documentManager;

  useEffect(() => {
    if (currentDocument) {
      setEditTitle(currentDocument.title);
    }
  }, [currentDocument]);

  useEffect(() => {
    if (isEditing && inputRef.current) {
      inputRef.current.focus();
      inputRef.current.select();
    }
  }, [isEditing]);

  const handleStartEdit = () => {
    if (!currentDocument) return;
    setIsEditing(true);
  };

  const handleSaveTitle = () => {
    if (!currentDocument || !editTitle.trim()) {
      setEditTitle(currentDocument?.title || '');
      setIsEditing(false);
      return;
    }

    if (editTitle.trim() !== currentDocument.title) {
      setCurrentTitle(editTitle.trim());
    }
    setIsEditing(false);
  };

  const handleCancelEdit = () => {
    setEditTitle(currentDocument?.title || '');
    setIsEditing(false);
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      handleSaveTitle();
    } else if (e.key === 'Escape') {
      handleCancelEdit();
    }
  };

  const getSaveStatus = () => {
    if (!isAuthenticated) return null;
    if (!currentDocument) return null;
    if (isSaving) return 'Saving...';
    if (hasUnsavedChanges) return 'Unsaved changes';
    return 'Saved';
  };

  const saveStatus = getSaveStatus();

  return (
    <div className="document-title-bar">
      <div className="title-section">
        {currentDocument ? (
          <>
            {isEditing ? (
              <input
                ref={inputRef}
                type="text"
                value={editTitle}
                onChange={(e) => setEditTitle(e.target.value)}
                onBlur={handleSaveTitle}
                onKeyDown={handleKeyDown}
                className="title-input"
                placeholder="Document title..."
              />
            ) : (
              <h1 
                className="document-title"
                onClick={handleStartEdit}
                title="Click to edit title"
              >
                {currentDocument.title}
              </h1>
            )}
          </>
        ) : (
          <h1 className="document-title untitled">
            Untitled Document
          </h1>
        )}
      </div>

      {saveStatus && (
        <div className={`save-status ${isSaving ? 'saving' : hasUnsavedChanges ? 'unsaved' : 'saved'}`}>
          <span className="status-indicator">
            {isSaving ? '⏳' : hasUnsavedChanges ? '●' : '✓'}
          </span>
          <span className="status-text">{saveStatus}</span>
        </div>
      )}

      <style jsx>{`
        .document-title-bar {
          display: flex;
          align-items: center;
          justify-content: space-between;
          padding: 8px 16px;
          background: #fafafa;
          border-bottom: 1px solid #e5e7eb;
          min-height: 48px;
        }

        .title-section {
          flex: 1;
          min-width: 0;
        }

        .document-title {
          margin: 0;
          font-size: 16px;
          font-weight: 500;
          color: #111827;
          cursor: text;
          padding: 4px 8px;
          border-radius: 4px;
          transition: background-color 0.15s;
          white-space: nowrap;
          overflow: hidden;
          text-overflow: ellipsis;
          max-width: 400px;
        }

        .document-title:hover {
          background: #f3f4f6;
        }

        .document-title.untitled {
          color: #6b7280;
          font-style: italic;
          cursor: default;
        }

        .document-title.untitled:hover {
          background: transparent;
        }

        .title-input {
          font-size: 16px;
          font-weight: 500;
          color: #111827;
          border: 2px solid #3b82f6;
          border-radius: 4px;
          padding: 4px 8px;
          background: white;
          outline: none;
          min-width: 200px;
          max-width: 400px;
        }

        .save-status {
          display: flex;
          align-items: center;
          gap: 4px;
          font-size: 12px;
          padding: 4px 8px;
          border-radius: 4px;
          white-space: nowrap;
        }

        .save-status.saving {
          color: #3b82f6;
          background: #eff6ff;
        }

        .save-status.unsaved {
          color: #f59e0b;
          background: #fffbeb;
        }

        .save-status.saved {
          color: #10b981;
          background: #ecfdf5;
        }

        .status-indicator {
          font-size: 10px;
          line-height: 1;
        }

        .status-text {
          font-weight: 500;
        }

        @media (max-width: 768px) {
          .document-title-bar {
            padding: 6px 12px;
          }

          .document-title,
          .title-input {
            font-size: 14px;
            max-width: 250px;
          }

          .save-status {
            font-size: 11px;
          }
        }
      `}</style>
    </div>
  );
};

export default DocumentTitleBar; 