import React from 'react';
import { useEditorContext } from '../contexts/EditorContext';
import { useAuth } from '../contexts/AuthContext';

interface DocumentTitleBarProps {
  title: string;
  onTitleChange: (title: string) => void;
  isEditing: boolean;
  onEditToggle: () => void;
}

const DocumentTitleBar: React.FC<DocumentTitleBarProps> = ({
  title,
  onTitleChange,
  isEditing,
  onEditToggle
}) => {
  const { documentManager } = useEditorContext();
  const { isAuthenticated } = useAuth();

  const { currentDocument, hasUnsavedChanges, isSaving, setCurrentTitle } = documentManager;

  const handleTitleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onEditToggle();
  };

  const handleStartEdit = () => {
    if (!currentDocument) return;
    onEditToggle();
  };

  const handleSaveTitle = () => {
    if (!currentDocument || !title.trim()) {
      onTitleChange(currentDocument?.title || '');
      onEditToggle();
      return;
    }

    if (title.trim() !== currentDocument.title) {
      setCurrentTitle(title.trim());
    }
    onEditToggle();
  };

  const handleCancelEdit = () => {
    onTitleChange(currentDocument?.title || '');
    onEditToggle();
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

  if (isEditing) {
    return (
      <div className="document-title-bar editing">
        <form onSubmit={handleTitleSubmit} className="title-edit-form">
          <input
            type="text"
            value={title}
            onChange={(e) => onTitleChange(e.target.value)}
            className="title-input"
            autoFocus
            onBlur={handleSaveTitle}
            onKeyDown={handleKeyDown}
          />
        </form>
      </div>
    );
  }

  return (
    <div className="document-title-bar">
      <h1 className="document-title" onClick={handleStartEdit}>
        {title || 'Untitled Document'}
      </h1>
      <button 
        className="edit-title-button" 
        onClick={handleStartEdit}
        aria-label="Edit title"
      >
        ✏️
      </button>

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
