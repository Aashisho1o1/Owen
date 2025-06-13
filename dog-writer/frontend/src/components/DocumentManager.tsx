import React, { useState } from 'react';
import { useDocuments } from '../hooks/useDocuments';
import { useAuth } from '../contexts/AuthContext';
import { Document } from '../services/api';

interface DocumentManagerProps {
  onDocumentSelect?: (document: Document) => void;
  onClose?: () => void;
  className?: string;
}

const DocumentManager: React.FC<DocumentManagerProps> = ({
  onDocumentSelect,
  onClose,
  className = '',
}) => {
  const { isAuthenticated } = useAuth();
  const {
    documents,
    isLoading,
    error,
    createDocument,
    deleteDocument,
    toggleFavorite,
    clearError,
    getWordCount,
  } = useDocuments();

  const [newDocTitle, setNewDocTitle] = useState('');
  const [showNewDocForm, setShowNewDocForm] = useState(false);
  const [deleteConfirm, setDeleteConfirm] = useState<string | null>(null);

  if (!isAuthenticated) {
    return (
      <div className={`document-manager ${className}`}>
        <div className="auth-prompt">
          <h3>Sign in to access your documents</h3>
          <p>Please log in to save and manage your writing documents.</p>
        </div>
      </div>
    );
  }

  const handleCreateDocument = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newDocTitle.trim()) return;

    const newDoc = await createDocument(newDocTitle.trim());
    if (newDoc && onDocumentSelect) {
      onDocumentSelect(newDoc);
    }
    
    setNewDocTitle('');
    setShowNewDocForm(false);
  };

  const handleDeleteDocument = async (id: string) => {
    if (deleteConfirm === id) {
      await deleteDocument(id);
      setDeleteConfirm(null);
    } else {
      setDeleteConfirm(id);
      // Auto-clear confirmation after 3 seconds
      setTimeout(() => setDeleteConfirm(null), 3000);
    }
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffTime = Math.abs(now.getTime() - date.getTime());
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));

    if (diffDays === 1) return 'Today';
    if (diffDays === 2) return 'Yesterday';
    if (diffDays <= 7) return `${diffDays - 1} days ago`;
    
    return date.toLocaleDateString();
  };

  const sortedDocuments = [...documents].sort((a, b) => {
    // Favorites first, then by last updated
    if (a.is_favorite && !b.is_favorite) return -1;
    if (!a.is_favorite && b.is_favorite) return 1;
    return new Date(b.updated_at).getTime() - new Date(a.updated_at).getTime();
  });

  return (
    <div className={`document-manager ${className}`}>
      {/* Header */}
      <div className="manager-header">
        <div className="header-content">
          <h2>My Documents</h2>
          {onClose && (
            <button 
              onClick={onClose}
              className="close-btn"
              aria-label="Close document manager"
            >
              ×
            </button>
          )}
        </div>
        
        <button 
          onClick={() => setShowNewDocForm(true)}
          className="new-doc-btn"
          disabled={isLoading}
        >
          + New Document
        </button>
      </div>

      {/* Error Message */}
      {error && (
        <div className="error-banner">
          <span>{error}</span>
          <button onClick={clearError}>×</button>
        </div>
      )}

      {/* New Document Form */}
      {showNewDocForm && (
        <form onSubmit={handleCreateDocument} className="new-doc-form">
          <div className="form-row">
            <input
              type="text"
              value={newDocTitle}
              onChange={(e) => setNewDocTitle(e.target.value)}
              placeholder="Document title..."
              autoFocus
              required
            />
            <button type="submit" disabled={!newDocTitle.trim()}>
              Create
            </button>
            <button 
              type="button" 
              onClick={() => {
                setShowNewDocForm(false);
                setNewDocTitle('');
              }}
            >
              Cancel
            </button>
          </div>
        </form>
      )}

      {/* Loading State */}
      {isLoading && (
        <div className="loading-state">
          <div className="loading-spinner"></div>
          <span>Loading documents...</span>
        </div>
      )}

      {/* Documents List */}
      <div className="documents-list">
        {sortedDocuments.length === 0 && !isLoading ? (
          <div className="empty-state">
            <h3>No documents yet</h3>
            <p>Create your first document to get started writing.</p>
          </div>
        ) : (
          sortedDocuments.map((doc) => (
            <div key={doc.id} className="document-item">
              <div 
                className="document-content"
                onClick={() => onDocumentSelect?.(doc)}
              >
                <div className="document-header">
                  <h3 className="document-title">
                    {doc.is_favorite && <span className="favorite-star">★</span>}
                    {doc.title}
                  </h3>
                  <div className="document-meta">
                    <span className="word-count">
                      {getWordCount(doc.content)} words
                    </span>
                    <span className="last-updated">
                      {formatDate(doc.updated_at)}
                    </span>
                  </div>
                </div>
                
                {doc.content && (
                  <p className="document-preview">
                    {doc.content.slice(0, 120)}
                    {doc.content.length > 120 ? '...' : ''}
                  </p>
                )}
              </div>
              
              <div className="document-actions">
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    toggleFavorite(doc.id);
                  }}
                  className={`favorite-btn ${doc.is_favorite ? 'active' : ''}`}
                  title={doc.is_favorite ? 'Remove from favorites' : 'Add to favorites'}
                >
                  ★
                </button>
                
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    handleDeleteDocument(doc.id);
                  }}
                  className={`delete-btn ${deleteConfirm === doc.id ? 'confirm' : ''}`}
                  title={deleteConfirm === doc.id ? 'Click again to confirm' : 'Delete document'}
                >
                  {deleteConfirm === doc.id ? '✓' : '🗑'}
                </button>
              </div>
            </div>
          ))
        )}
      </div>

      <style jsx>{`
        .document-manager {
          background: white;
          border-radius: 8px;
          box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
          overflow: hidden;
          max-height: 80vh;
          display: flex;
          flex-direction: column;
        }

        .manager-header {
          padding: 20px;
          border-bottom: 1px solid #e5e7eb;
          background: #f9fafb;
        }

        .header-content {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 12px;
        }

        .header-content h2 {
          margin: 0;
          font-size: 1.25rem;
          font-weight: 600;
          color: #111827;
        }

        .close-btn {
          background: none;
          border: none;
          font-size: 24px;
          cursor: pointer;
          color: #6b7280;
          padding: 4px;
          line-height: 1;
        }

        .close-btn:hover {
          color: #374151;
        }

        .new-doc-btn {
          background: #3b82f6;
          color: white;
          border: none;
          padding: 8px 16px;
          border-radius: 6px;
          cursor: pointer;
          font-size: 14px;
          font-weight: 500;
        }

        .new-doc-btn:hover:not(:disabled) {
          background: #2563eb;
        }

        .new-doc-btn:disabled {
          opacity: 0.5;
          cursor: not-allowed;
        }

        .error-banner {
          background: #fef2f2;
          color: #dc2626;
          padding: 12px 20px;
          display: flex;
          justify-content: space-between;
          align-items: center;
          border-bottom: 1px solid #fecaca;
        }

        .error-banner button {
          background: none;
          border: none;
          color: #dc2626;
          cursor: pointer;
          font-size: 18px;
          padding: 0;
        }

        .new-doc-form {
          padding: 16px 20px;
          border-bottom: 1px solid #e5e7eb;
          background: #f9fafb;
        }

        .form-row {
          display: flex;
          gap: 8px;
          align-items: center;
        }

        .form-row input {
          flex: 1;
          padding: 8px 12px;
          border: 1px solid #d1d5db;
          border-radius: 4px;
          font-size: 14px;
        }

        .form-row button {
          padding: 8px 12px;
          border: 1px solid #d1d5db;
          border-radius: 4px;
          cursor: pointer;
          font-size: 14px;
        }

        .form-row button[type="submit"] {
          background: #3b82f6;
          color: white;
          border-color: #3b82f6;
        }

        .form-row button[type="submit"]:disabled {
          opacity: 0.5;
          cursor: not-allowed;
        }

        .loading-state {
          padding: 40px 20px;
          text-align: center;
          color: #6b7280;
          display: flex;
          flex-direction: column;
          align-items: center;
          gap: 12px;
        }

        .loading-spinner {
          width: 20px;
          height: 20px;
          border: 2px solid #e5e7eb;
          border-top: 2px solid #3b82f6;
          border-radius: 50%;
          animation: spin 1s linear infinite;
        }

        @keyframes spin {
          0% { transform: rotate(0deg); }
          100% { transform: rotate(360deg); }
        }

        .documents-list {
          flex: 1;
          overflow-y: auto;
          padding: 8px;
        }

        .empty-state {
          padding: 60px 20px;
          text-align: center;
          color: #6b7280;
        }

        .empty-state h3 {
          margin: 0 0 8px 0;
          color: #374151;
        }

        .empty-state p {
          margin: 0;
          font-size: 14px;
        }

        .document-item {
          display: flex;
          align-items: flex-start;
          padding: 12px;
          border-radius: 6px;
          margin-bottom: 4px;
          cursor: pointer;
          transition: background-color 0.15s;
        }

        .document-item:hover {
          background: #f3f4f6;
        }

        .document-content {
          flex: 1;
          min-width: 0;
        }

        .document-header {
          display: flex;
          justify-content: space-between;
          align-items: flex-start;
          margin-bottom: 4px;
        }

        .document-title {
          margin: 0;
          font-size: 14px;
          font-weight: 500;
          color: #111827;
          display: flex;
          align-items: center;
          gap: 4px;
        }

        .favorite-star {
          color: #fbbf24;
          font-size: 12px;
        }

        .document-meta {
          display: flex;
          gap: 12px;
          font-size: 12px;
          color: #6b7280;
          white-space: nowrap;
        }

        .document-preview {
          margin: 0;
          font-size: 13px;
          color: #6b7280;
          line-height: 1.4;
        }

        .document-actions {
          display: flex;
          gap: 4px;
          margin-left: 12px;
        }

        .document-actions button {
          background: none;
          border: none;
          padding: 4px;
          cursor: pointer;
          border-radius: 4px;
          font-size: 14px;
          opacity: 0.6;
          transition: opacity 0.15s;
        }

        .document-actions button:hover {
          opacity: 1;
        }

        .favorite-btn.active {
          color: #fbbf24;
          opacity: 1;
        }

        .delete-btn.confirm {
          background: #dc2626;
          color: white;
          opacity: 1;
        }

        .auth-prompt {
          padding: 60px 20px;
          text-align: center;
          color: #6b7280;
        }

        .auth-prompt h3 {
          margin: 0 0 8px 0;
          color: #374151;
        }

        .auth-prompt p {
          margin: 0;
          font-size: 14px;
        }
      `}</style>
    </div>
  );
};

export default DocumentManager; 