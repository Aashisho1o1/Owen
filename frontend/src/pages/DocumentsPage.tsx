// Template Fix Deployment - 2024
import React, { useState, useEffect } from 'react';
import { Navigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { useUIContext } from '../contexts/UIContext';
import DocumentManager from '../components/DocumentManager';
import { Document } from '../services/api';


import './DocumentsPage.css';

const DocumentsPage: React.FC = () => {
  const { user, isAuthenticated } = useAuth();
  const { setShowAuthModal, setAuthMode } = useUIContext();
  
  const [view, setView] = useState<'grid' | 'list'>('grid');
  const [searchTerm, setSearchTerm] = useState('');
  const [sortBy, setSortBy] = useState<'updated' | 'created' | 'title' | 'words'>('updated');
  const [selectedDocuments, setSelectedDocuments] = useState<Set<string>>(new Set());
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [editingDocument, setEditingDocument] = useState<string | null>(null);
  const [newTitle, setNewTitle] = useState('');

  useEffect(() => {
    refreshAll();
  }, [refreshAll]);

  const handleCreateFromTemplate = async (template: any) => {
    if (!isAuthenticated) {
      setAuthMode('signin');
      setShowAuthModal(true);
      return;
    }

    try {
      const newDoc = await createFromTemplate(template.id, `New ${template.title}`);
      navigate(`/editor/${newDoc.id}`);
    } catch (error) {
      console.error('Failed to create document from template:', error);
      alert('Failed to create document. Please try again.');
    }
  };

  const handleCreateBlankDocument = async () => {
    if (!isAuthenticated) {
      setAuthMode('signin');
      setShowAuthModal(true);
      return;
    }

    try {
      const newDoc = await createDocument('Untitled Document', 'novel');
      navigate(`/editor/${newDoc.id}`);
    } catch (error) {
      console.error('Failed to create blank document:', error);
      alert('Failed to create document. Please try again.');
    }
  };

  const handleDeleteSelected = async () => {
    try {
      for (const docId of selectedDocuments) {
        await deleteDocument(docId);
      }
      setSelectedDocuments(new Set());
      setShowDeleteModal(false);
      refreshAll();
    } catch (error) {
      console.error('Failed to delete documents:', error);
    }
  };

  const handleRenameDocument = async (docId: string, newTitle: string) => {
    try {
      await updateDocument(docId, { title: newTitle });
      setEditingDocument(null);
      setNewTitle('');
      refreshAll();
    } catch (error) {
      console.error('Failed to rename document:', error);
    }
  };

  const filteredDocuments = documents.filter(doc =>
    doc.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
    doc.content.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const sortedDocuments = [...filteredDocuments].sort((a, b) => {
    switch (sortBy) {
      case 'title':
        return a.title.localeCompare(b.title);
      case 'created':
        return new Date(b.created_at).getTime() - new Date(a.created_at).getTime();
      case 'words':
        return (b.word_count || 0) - (a.word_count || 0);
      case 'updated':
      default:
        return new Date(b.updated_at).getTime() - new Date(a.updated_at).getTime();
    }
  });

  const recentDocuments = getRecentDocuments(5);

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffTime = Math.abs(now.getTime() - date.getTime());
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    
    if (diffDays === 1) return 'Today';
    if (diffDays === 2) return 'Yesterday';
    if (diffDays <= 7) return `${diffDays} days ago`;
    return date.toLocaleDateString();
  };

  const formatWordCount = (wordCount: number) => {
    if (wordCount >= 1000) {
      return `${(wordCount / 1000).toFixed(1)}k words`;
    }
    return `${wordCount} words`;
  };

  if (isLoading) {
    return (
      <div className="documents-page loading">
        <div className="loading-spinner">
          <div className="spinner"></div>
          <p>Loading your documents...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="documents-page">
      <div className="documents-header">
        <div className="header-content">
          <h1>Start a new document</h1>
          {!isAuthenticated && (
            <p className="auth-notice">
              <span className="auth-icon">🔒</span>
              Please <button className="inline-auth-btn" onClick={() => { setAuthMode('signin'); setShowAuthModal(true); }}>sign in</button> to create and save documents
            </p>
          )}
          <div className="template-gallery">
            {/* Blank Document */}
            <div 
              className="template-card blank"
              onClick={handleCreateBlankDocument}
            >
              <div className="template-preview">
                <div className="blank-icon">+</div>
              </div>
              <h3>Blank document</h3>
            </div>

            {/* Story Genre Templates */}
            {templates.map((template) => {
              // Map template IDs to genre icons and display names
              const getTemplateIcon = (id: string) => {
                switch(id) {
                  case 'romance': return '💕';
                  case 'fantasy': return '🐉';
                  case 'mystery': return '🔍';
                  case 'scifi': return '🚀';
                  case 'horror': return '👻';
                  default: return '✍️'; // Elegant writing icon instead of book
                }
              };

              const getGenreDisplayName = (id: string) => {
                switch(id) {
                  case 'romance': return 'Romance';
                  case 'fantasy': return 'Fantasy';
                  case 'mystery': return 'Mystery';
                  case 'scifi': return 'Sci-Fi';
                  case 'horror': return 'Horror';
                  default: return 'Template';
                }
              };

              return (
                <div 
                  key={template.id}
                  className="template-card"
                  data-template-id={template.id}
                  onClick={() => handleCreateFromTemplate(template)}
                >
                  <div className="template-preview">
                    <div className="template-icon">{getTemplateIcon(template.id)}</div>
                    <div className="template-content">
                      <p>{template.description}</p>
                    </div>
                  </div>
                  <h3>{template.title}</h3>
                </div>
              );
            })}
          </div>
        </div>
      </div>

      <div className="documents-main">
        <div className="documents-controls">
          <div className="controls-left">
            <h2>Recent documents</h2>
            <div className="document-stats">
              {documents.length} documents
            </div>
          </div>
          
          <div className="controls-right">
            <div className="search-box">
              <input
                type="text"
                placeholder="Search documents..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="search-input"
              />
            </div>
            
            <select 
              value={sortBy} 
              onChange={(e) => setSortBy(e.target.value as any)}
              className="sort-select"
            >
              <option value="updated">Last modified</option>
              <option value="created">Date created</option>
              <option value="title">Title</option>
              <option value="words">Word count</option>
            </select>
            
            <div className="view-controls">
              <button 
                className={`view-btn ${view === 'grid' ? 'active' : ''}`}
                onClick={() => setView('grid')}
              >
                ⊞
              </button>
              <button 
                className={`view-btn ${view === 'list' ? 'active' : ''}`}
                onClick={() => setView('list')}
              >
                ☰
              </button>
            </div>
          </div>
        </div>

        {selectedDocuments.size > 0 && (
          <div className="selection-bar">
            <span>{selectedDocuments.size} document(s) selected</span>
            <button 
              className="delete-btn"
              onClick={() => setShowDeleteModal(true)}
            >
              Delete
            </button>
            <button 
              className="clear-selection-btn"
              onClick={() => setSelectedDocuments(new Set())}
            >
              Clear selection
            </button>
          </div>
        )}

        <div className={`documents-grid ${view}`}>
          {sortedDocuments.map((doc) => (
            <div 
              key={doc.id} 
              className={`document-card ${selectedDocuments.has(doc.id) ? 'selected' : ''}`}
            >
              <div className="document-preview">
                <div className="document-content">
                  {doc.content.slice(0, 150) || 'No content yet...'}
                </div>
              </div>
              
              <div className="document-info">
                <div className="document-header">
                  {editingDocument === doc.id ? (
                    <input
                      type="text"
                      value={newTitle}
                      onChange={(e) => setNewTitle(e.target.value)}
                      onBlur={() => handleRenameDocument(doc.id, newTitle)}
                      onKeyPress={(e) => {
                        if (e.key === 'Enter') {
                          handleRenameDocument(doc.id, newTitle);
                        }
                      }}
                      autoFocus
                      className="title-input"
                    />
                  ) : (
                    <h3 
                      className="document-title"
                      onClick={() => navigate(`/editor/${doc.id}`)}
                    >
                      {doc.title}
                    </h3>
                  )}
                  
                  <div className="document-actions">
                    <button
                      className="action-btn"
                      onClick={(e) => {
                        e.stopPropagation();
                        setEditingDocument(doc.id);
                        setNewTitle(doc.title);
                      }}
                    >
                      ✏️
                    </button>
                    <button
                      className="action-btn"
                      onClick={(e) => {
                        e.stopPropagation();
                        const newSelection = new Set(selectedDocuments);
                        if (newSelection.has(doc.id)) {
                          newSelection.delete(doc.id);
                        } else {
                          newSelection.add(doc.id);
                        }
                        setSelectedDocuments(newSelection);
                      }}
                    >
                      {selectedDocuments.has(doc.id) ? '☑️' : '☐'}
                    </button>
                  </div>
                </div>
                
                <div className="document-meta">
                  <span className="last-modified">
                    Last modified: {formatDate(doc.updated_at)}
                  </span>
                  <span className="word-count">
                    {formatWordCount(doc.word_count || 0)}
                  </span>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Delete Confirmation Modal */}
      {showDeleteModal && (
        <div className="modal-overlay">
          <div className="modal">
            <h3>Delete Documents</h3>
            <p>Are you sure you want to delete {selectedDocuments.size} document(s)? This action cannot be undone.</p>
            <div className="modal-actions">
              <button 
                className="cancel-btn"
                onClick={() => setShowDeleteModal(false)}
              >
                Cancel
              </button>
              <button 
                className="delete-btn"
                onClick={handleDeleteSelected}
              >
                Delete
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default DocumentsPage;