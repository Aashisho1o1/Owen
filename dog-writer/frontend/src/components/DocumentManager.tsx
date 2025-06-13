import React, { useState, useEffect } from 'react';
import { useDocuments } from '../hooks/useDocuments';
import { useAuth } from '../contexts/AuthContext';
import { Document, DocumentFolder, DocumentSeries } from '../services/api';
import './DocumentManager.css';

interface DocumentManagerProps {
  onDocumentSelect: (document: Document) => void;
  onClose: () => void;
}

type ViewMode = 'documents' | 'folders' | 'series' | 'templates' | 'search' | 'analytics' | 'versions';
type SortBy = 'title' | 'updated_at' | 'created_at' | 'word_count';
type FilterBy = 'all' | 'novel' | 'chapter' | 'character_sheet' | 'outline' | 'notes';

const DocumentManager: React.FC<DocumentManagerProps> = ({ onDocumentSelect, onClose }) => {
  const { user } = useAuth();
  const {
    documents,
    folders,
    series,
    templates,
    versions,
    searchResults,
    writingStats,
    writingSessions,
    currentDocument,
    isLoading,
    isLoadingVersions,
    isSearching,
    error,
    createDocument,
    createFolder,
    createSeries,
    deleteDocument,
    deleteFolder,
    deleteSeries,
    duplicateDocument,
    moveDocument,
    searchDocuments,
    clearSearch,
    createFromTemplate,
    exportDocument,
    loadVersions,
    restoreVersion,
    loadWritingStats,
    shareDocument,
    getDocumentsByFolder,
    getDocumentsBySeries,
    getFolderTree,
    getRecentDocuments,
    getTotalWordCount,
    getWordCount,
    refreshAll
  } = useDocuments();

  const [viewMode, setViewMode] = useState<ViewMode>('documents');
  const [selectedFolder, setSelectedFolder] = useState<string | null>(null);
  const [selectedSeries, setSelectedSeries] = useState<string | null>(null);
  const [sortBy, setSortBy] = useState<SortBy>('updated_at');
  const [filterBy, setFilterBy] = useState<FilterBy>('all');
  const [searchQuery, setSearchQuery] = useState('');
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showFolderModal, setShowFolderModal] = useState(false);
  const [showSeriesModal, setShowSeriesModal] = useState(false);
  const [showExportModal, setShowExportModal] = useState(false);
  const [showShareModal, setShowShareModal] = useState(false);
  const [showVersionModal, setShowVersionModal] = useState(false);
  const [selectedDocumentId, setSelectedDocumentId] = useState<string | null>(null);
  const [newItemName, setNewItemName] = useState('');
  const [newItemDescription, setNewItemDescription] = useState('');

  // Authentication check
  if (!user) {
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
  }

  // Sort and filter documents
  const getDisplayDocuments = () => {
    let displayDocs = documents;

    // Filter by folder/series
    if (selectedFolder) {
      displayDocs = getDocumentsByFolder(selectedFolder);
    } else if (selectedSeries) {
      displayDocs = getDocumentsBySeries(selectedSeries);
    }

    // Filter by type
    if (filterBy !== 'all') {
      displayDocs = displayDocs.filter(doc => doc.document_type === filterBy);
    }

    // Sort documents
    displayDocs.sort((a, b) => {
      switch (sortBy) {
        case 'title':
          return a.title.localeCompare(b.title);
        case 'created_at':
          return new Date(b.created_at).getTime() - new Date(a.created_at).getTime();
        case 'word_count':
          return (b.word_count || 0) - (a.word_count || 0);
        case 'updated_at':
        default:
          return new Date(b.updated_at).getTime() - new Date(a.updated_at).getTime();
      }
    });

    return displayDocs;
  };

  // Handle search
  const handleSearch = async () => {
    if (!searchQuery.trim()) {
      clearSearch();
      return;
    }

    await searchDocuments({
      query: searchQuery,
      document_types: filterBy !== 'all' ? [filterBy] : undefined,
      folder_ids: selectedFolder ? [selectedFolder] : undefined,
      series_ids: selectedSeries ? [selectedSeries] : undefined
    });
    setViewMode('search');
  };

  // Create new document
  const handleCreateDocument = async (templateId?: string) => {
    if (!newItemName.trim()) return;

    try {
      let newDoc: Document;
      if (templateId) {
        newDoc = await createFromTemplate(templateId, newItemName, selectedFolder || undefined);
      } else {
        newDoc = await createDocument(
          newItemName,
          filterBy !== 'all' ? filterBy : 'novel',
          selectedFolder || undefined,
          selectedSeries || undefined
        );
      }
      setShowCreateModal(false);
      setNewItemName('');
      onDocumentSelect(newDoc);
    } catch (error) {
      console.error('Failed to create document:', error);
    }
  };

  // Export document
  const handleExport = async (documentId: string, format: string) => {
    try {
      await exportDocument(documentId, format);
      setShowExportModal(false);
    } catch (error) {
      console.error('Export failed:', error);
    }
  };

  // Load analytics
  useEffect(() => {
    if (viewMode === 'analytics') {
      loadWritingStats('month');
    }
  }, [viewMode, loadWritingStats]);

  // Format file size
  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  // Format date
  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString();
  };

  // Get document icon
  const getDocumentIcon = (type?: string) => {
    switch (type) {
      case 'novel': return '📖';
      case 'chapter': return '📃';
      case 'character_sheet': return '👤';
      case 'outline': return '📋';
      case 'notes': return '📝';
      default: return '📄';
    }
  };

  return (
    <div className="document-manager-overlay">
      <div className="document-manager">
        {/* Header */}
        <div className="document-manager-header">
          <h2>📄 Document Manager</h2>
          <div className="header-actions">
            <div className="total-stats">
              {documents.length} docs • {getTotalWordCount().toLocaleString()} words
            </div>
            <button onClick={onClose} className="close-button">✕</button>
          </div>
        </div>

        {/* Navigation */}
        <div className="document-nav">
          <button 
            className={viewMode === 'documents' ? 'active' : ''}
            onClick={() => setViewMode('documents')}
          >
            📄 Documents
          </button>
          <button 
            className={viewMode === 'folders' ? 'active' : ''}
            onClick={() => setViewMode('folders')}
          >
            📁 Folders
          </button>
          <button 
            className={viewMode === 'series' ? 'active' : ''}
            onClick={() => setViewMode('series')}
          >
            📚 Series
          </button>
          <button 
            className={viewMode === 'templates' ? 'active' : ''}
            onClick={() => setViewMode('templates')}
          >
            📋 Templates
          </button>
          <button 
            className={viewMode === 'analytics' ? 'active' : ''}
            onClick={() => setViewMode('analytics')}
          >
            📊 Analytics
          </button>
        </div>

        {/* Search Bar */}
        <div className="search-section">
          <div className="search-input-group">
            <input
              type="text"
              placeholder="Search your writing..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
              className="search-input"
            />
            <button onClick={handleSearch} disabled={isSearching} className="search-button">
              {isSearching ? '⏳' : '🔍'}
            </button>
            {searchResults.length > 0 && (
              <button onClick={clearSearch} className="clear-search-button">✕</button>
            )}
          </div>
        </div>

        {/* Controls */}
        <div className="document-controls">
          <div className="controls-left">
            <select value={filterBy} onChange={(e) => setFilterBy(e.target.value as FilterBy)}>
              <option value="all">All Types</option>
              <option value="novel">📖 Novels</option>
              <option value="chapter">📃 Chapters</option>
              <option value="character_sheet">👤 Characters</option>
              <option value="outline">📋 Outlines</option>
              <option value="notes">📝 Notes</option>
            </select>
            <select value={sortBy} onChange={(e) => setSortBy(e.target.value as SortBy)}>
              <option value="updated_at">Recently Updated</option>
              <option value="created_at">Recently Created</option>
              <option value="title">Title A-Z</option>
              <option value="word_count">Word Count</option>
            </select>
          </div>
          <div className="controls-right">
            <button onClick={() => setShowCreateModal(true)} className="create-button">
              ➕ New Document
            </button>
            {viewMode === 'folders' && (
              <button onClick={() => setShowFolderModal(true)} className="create-button">
                📁 New Folder
              </button>
            )}
            {viewMode === 'series' && (
              <button onClick={() => setShowSeriesModal(true)} className="create-button">
                📚 New Series
              </button>
            )}
          </div>
        </div>

        {/* Content */}
        <div className="document-content">
          {error && (
            <div className="error-message">
              ⚠️ {error}
            </div>
          )}

          {/* Documents View */}
          {viewMode === 'documents' && (
            <div className="documents-grid">
              {/* Recent Documents */}
              <div className="recent-section">
                <h3>🕒 Recent Documents</h3>
                <div className="document-list">
                  {getRecentDocuments(5).map(doc => (
                    <div key={doc.id} className="document-item" onClick={() => onDocumentSelect(doc)}>
                      <div className="document-icon">{getDocumentIcon(doc.document_type)}</div>
                      <div className="document-info">
                        <div className="document-title">{doc.title}</div>
                        <div className="document-meta">
                          {(doc.word_count || 0).toLocaleString()} words • {formatDate(doc.updated_at)}
                        </div>
                      </div>
                      <div className="document-actions">
                        <button onClick={(e) => { e.stopPropagation(); setSelectedDocumentId(doc.id); setShowVersionModal(true); loadVersions(doc.id); }}>
                          📝 Versions
                        </button>
                        <button onClick={(e) => { e.stopPropagation(); setSelectedDocumentId(doc.id); setShowExportModal(true); }}>
                          📤 Export
                        </button>
                        <button onClick={(e) => { e.stopPropagation(); setSelectedDocumentId(doc.id); setShowShareModal(true); }}>
                          🔗 Share
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* All Documents */}
              <div className="all-documents-section">
                <h3>📄 All Documents ({getDisplayDocuments().length})</h3>
                <div className="document-list">
                  {getDisplayDocuments().map(doc => (
                    <div key={doc.id} className="document-item" onClick={() => onDocumentSelect(doc)}>
                      <div className="document-icon">{getDocumentIcon(doc.document_type)}</div>
                      <div className="document-info">
                        <div className="document-title">{doc.title}</div>
                        <div className="document-meta">
                          {(doc.word_count || 0).toLocaleString()} words • {formatDate(doc.updated_at)}
                          {doc.series_id && (
                            <span className="series-badge">
                              📚 {series.find(s => s.id === doc.series_id)?.name}
                            </span>
                          )}
                          {doc.folder_id && (
                            <span className="folder-badge">
                              📁 {folders.find(f => f.id === doc.folder_id)?.name}
                            </span>
                          )}
                        </div>
                      </div>
                      <div className="document-actions">
                        <button onClick={(e) => { e.stopPropagation(); duplicateDocument(doc.id); }}>
                          📋 Duplicate
                        </button>
                        <button onClick={(e) => { e.stopPropagation(); setSelectedDocumentId(doc.id); setShowVersionModal(true); loadVersions(doc.id); }}>
                          📝 Versions
                        </button>
                        <button onClick={(e) => { e.stopPropagation(); setSelectedDocumentId(doc.id); setShowExportModal(true); }}>
                          📤 Export
                        </button>
                        <button onClick={(e) => { e.stopPropagation(); deleteDocument(doc.id); }} className="delete-button">
                          🗑️ Delete
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}

          {/* Folders View */}
          {viewMode === 'folders' && (
            <div className="folders-grid">
              {getFolderTree().map(folder => (
                <div key={folder.id} className="folder-item" onClick={() => setSelectedFolder(folder.id)}>
                  <div className="folder-icon" style={{ color: folder.color }}>📁</div>
                  <div className="folder-info">
                    <div className="folder-name">{folder.name}</div>
                    <div className="folder-meta">
                      {getDocumentsByFolder(folder.id).length} documents
                    </div>
                  </div>
                  <div className="folder-actions">
                    <button onClick={(e) => { e.stopPropagation(); deleteFolder(folder.id); }} className="delete-button">
                      🗑️ Delete
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}

          {/* Series View */}
          {viewMode === 'series' && (
            <div className="series-grid">
              {series.map(seriesItem => (
                <div key={seriesItem.id} className="series-item" onClick={() => setSelectedSeries(seriesItem.id)}>
                  <div className="series-icon">📚</div>
                  <div className="series-info">
                    <div className="series-name">{seriesItem.name}</div>
                    <div className="series-meta">
                      {getDocumentsBySeries(seriesItem.id).length} documents • 
                      {seriesItem.total_word_count?.toLocaleString() || 0} words
                    </div>
                    {seriesItem.description && (
                      <div className="series-description">{seriesItem.description}</div>
                    )}
                  </div>
                  <div className="series-actions">
                    <button onClick={(e) => { e.stopPropagation(); deleteSeries(seriesItem.id); }} className="delete-button">
                      🗑️ Delete
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}

          {/* Templates View */}
          {viewMode === 'templates' && (
            <div className="templates-grid">
              {templates.map(template => (
                <div key={template.id} className="template-item">
                  <div className="template-icon">{getDocumentIcon(template.document_type)}</div>
                  <div className="template-info">
                    <div className="template-name">{template.name}</div>
                    <div className="template-preview">{template.preview_text}</div>
                  </div>
                  <div className="template-actions">
                    <button onClick={() => { setNewItemName(`New ${template.name}`); handleCreateDocument(template.id); }}>
                      ➕ Use Template
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}

          {/* Search Results */}
          {viewMode === 'search' && (
            <div className="search-results">
              <h3>🔍 Search Results ({searchResults.length})</h3>
              {searchResults.map(result => {
                const doc = documents.find(d => d.id === result.document_id);
                return (
                  <div key={result.document_id} className="search-result-item" onClick={() => doc && onDocumentSelect(doc)}>
                    <div className="result-title">{result.document_title}</div>
                    <div className="result-matches">
                      {result.matches.map((match, idx) => (
                        <div key={idx} className="result-match">
                          ...{match.context}...
                        </div>
                      ))}
                    </div>
                  </div>
                );
              })}
            </div>
          )}

          {/* Analytics View */}
          {viewMode === 'analytics' && (
            <div className="analytics-view">
              <div className="analytics-grid">
                <div className="stat-card">
                  <h4>📊 Writing Statistics</h4>
                  <div className="stat-value">{getTotalWordCount().toLocaleString()}</div>
                  <div className="stat-label">Total Words</div>
                </div>
                <div className="stat-card">
                  <h4>📄 Document Count</h4>
                  <div className="stat-value">{documents.length}</div>
                  <div className="stat-label">Total Documents</div>
                </div>
                <div className="stat-card">
                  <h4>📚 Series Count</h4>
                  <div className="stat-value">{series.length}</div>
                  <div className="stat-label">Active Series</div>
                </div>
                <div className="stat-card">
                  <h4>📁 Folders</h4>
                  <div className="stat-value">{folders.length}</div>
                  <div className="stat-label">Organized Folders</div>
                </div>
              </div>
              
              {writingStats && (
                <div className="writing-insights">
                  <h4>📈 Monthly Insights</h4>
                  <p>Average words per day: {Math.round(writingStats.avg_words_per_day || 0)}</p>
                  <p>Most productive day: {writingStats.most_productive_day || 'N/A'}</p>
                  <p>Total writing sessions: {writingStats.total_sessions || 0}</p>
                </div>
              )}
            </div>
          )}
        </div>

        {/* Modals */}
        {showCreateModal && (
          <div className="modal-overlay">
            <div className="modal">
              <h3>Create New Document</h3>
              <input
                type="text"
                placeholder="Document title..."
                value={newItemName}
                onChange={(e) => setNewItemName(e.target.value)}
                autoFocus
              />
              <div className="modal-actions">
                <button onClick={() => handleCreateDocument()} disabled={!newItemName.trim()}>
                  Create
                </button>
                <button onClick={() => { setShowCreateModal(false); setNewItemName(''); }}>
                  Cancel
                </button>
              </div>
            </div>
          </div>
        )}

        {showFolderModal && (
          <div className="modal-overlay">
            <div className="modal">
              <h3>Create New Folder</h3>
              <input
                type="text"
                placeholder="Folder name..."
                value={newItemName}
                onChange={(e) => setNewItemName(e.target.value)}
                autoFocus
              />
              <div className="modal-actions">
                <button onClick={async () => { 
                  await createFolder(newItemName); 
                  setShowFolderModal(false); 
                  setNewItemName(''); 
                }} disabled={!newItemName.trim()}>
                  Create
                </button>
                <button onClick={() => { setShowFolderModal(false); setNewItemName(''); }}>
                  Cancel
                </button>
              </div>
            </div>
          </div>
        )}

        {showSeriesModal && (
          <div className="modal-overlay">
            <div className="modal">
              <h3>Create New Series</h3>
              <input
                type="text"
                placeholder="Series name..."
                value={newItemName}
                onChange={(e) => setNewItemName(e.target.value)}
                autoFocus
              />
              <textarea
                placeholder="Series description (optional)..."
                value={newItemDescription}
                onChange={(e) => setNewItemDescription(e.target.value)}
              />
              <div className="modal-actions">
                <button onClick={async () => { 
                  await createSeries(newItemName, newItemDescription || undefined); 
                  setShowSeriesModal(false); 
                  setNewItemName(''); 
                  setNewItemDescription('');
                }} disabled={!newItemName.trim()}>
                  Create
                </button>
                <button onClick={() => { 
                  setShowSeriesModal(false); 
                  setNewItemName(''); 
                  setNewItemDescription('');
                }}>
                  Cancel
                </button>
              </div>
            </div>
          </div>
        )}

        {showExportModal && selectedDocumentId && (
          <div className="modal-overlay">
            <div className="modal">
              <h3>Export Document</h3>
              <div className="export-options">
                <button onClick={() => handleExport(selectedDocumentId, 'pdf')}>
                  📄 Export as PDF
                </button>
                <button onClick={() => handleExport(selectedDocumentId, 'docx')}>
                  📝 Export as DOCX
                </button>
                <button onClick={() => handleExport(selectedDocumentId, 'epub')}>
                  📖 Export as EPUB
                </button>
                <button onClick={() => handleExport(selectedDocumentId, 'txt')}>
                  📃 Export as TXT
                </button>
              </div>
              <div className="modal-actions">
                <button onClick={() => { setShowExportModal(false); setSelectedDocumentId(null); }}>
                  Cancel
                </button>
              </div>
            </div>
          </div>
        )}

        {showVersionModal && selectedDocumentId && (
          <div className="modal-overlay">
            <div className="modal version-modal">
              <h3>📝 Version History</h3>
              {isLoadingVersions ? (
                <div className="loading">Loading versions...</div>
              ) : (
                <div className="versions-list">
                  {versions.map(version => (
                    <div key={version.id} className="version-item">
                      <div className="version-info">
                        <div className="version-number">v{version.version_number}</div>
                        <div className="version-date">{formatDate(version.created_at)}</div>
                        <div className="version-words">{version.word_count?.toLocaleString()} words</div>
                        <div className="version-summary">{version.change_summary}</div>
                      </div>
                      <div className="version-actions">
                        <button onClick={() => restoreVersion(selectedDocumentId, version.id)}>
                          🔄 Restore
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              )}
              <div className="modal-actions">
                <button onClick={() => { setShowVersionModal(false); setSelectedDocumentId(null); }}>
                  Close
                </button>
              </div>
            </div>
          </div>
        )}

        {isLoading && (
          <div className="loading-overlay">
            <div className="loading-spinner">📄 Loading...</div>
          </div>
        )}
      </div>
    </div>
  );
};

export default DocumentManager; 
import { useDocuments } from '../hooks/useDocuments';
import { useAuth } from '../contexts/AuthContext';
import { Document, DocumentFolder, DocumentSeries } from '../services/api';
import './DocumentManager.css';

interface DocumentManagerProps {
  onDocumentSelect: (document: Document) => void;
  onClose: () => void;
}

type ViewMode = 'documents' | 'folders' | 'series' | 'templates' | 'search' | 'analytics' | 'versions';
type SortBy = 'title' | 'updated_at' | 'created_at' | 'word_count';
type FilterBy = 'all' | 'novel' | 'chapter' | 'character_sheet' | 'outline' | 'notes';

const DocumentManager: React.FC<DocumentManagerProps> = ({ onDocumentSelect, onClose }) => {
  const { user } = useAuth();
  const {
    documents,
    folders,
    series,
    templates,
    versions,
    searchResults,
    writingStats,
    writingSessions,
    currentDocument,
    isLoading,
    isLoadingVersions,
    isSearching,
    error,
    createDocument,
    createFolder,
    createSeries,
    deleteDocument,
    deleteFolder,
    deleteSeries,
    duplicateDocument,
    moveDocument,
    searchDocuments,
    clearSearch,
    createFromTemplate,
    exportDocument,
    loadVersions,
    restoreVersion,
    loadWritingStats,
    shareDocument,
    getDocumentsByFolder,
    getDocumentsBySeries,
    getFolderTree,
    getRecentDocuments,
    getTotalWordCount,
    getWordCount,
    refreshAll
  } = useDocuments();

  const [viewMode, setViewMode] = useState<ViewMode>('documents');
  const [selectedFolder, setSelectedFolder] = useState<string | null>(null);
  const [selectedSeries, setSelectedSeries] = useState<string | null>(null);
  const [sortBy, setSortBy] = useState<SortBy>('updated_at');
  const [filterBy, setFilterBy] = useState<FilterBy>('all');
  const [searchQuery, setSearchQuery] = useState('');
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showFolderModal, setShowFolderModal] = useState(false);
  const [showSeriesModal, setShowSeriesModal] = useState(false);
  const [showExportModal, setShowExportModal] = useState(false);
  const [showShareModal, setShowShareModal] = useState(false);
  const [showVersionModal, setShowVersionModal] = useState(false);
  const [selectedDocumentId, setSelectedDocumentId] = useState<string | null>(null);
  const [newItemName, setNewItemName] = useState('');
  const [newItemDescription, setNewItemDescription] = useState('');

  // Authentication check
  if (!user) {
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
  }

  // Sort and filter documents
  const getDisplayDocuments = () => {
    let displayDocs = documents;

    // Filter by folder/series
    if (selectedFolder) {
      displayDocs = getDocumentsByFolder(selectedFolder);
    } else if (selectedSeries) {
      displayDocs = getDocumentsBySeries(selectedSeries);
    }

    // Filter by type
    if (filterBy !== 'all') {
      displayDocs = displayDocs.filter(doc => doc.document_type === filterBy);
    }

    // Sort documents
    displayDocs.sort((a, b) => {
      switch (sortBy) {
        case 'title':
          return a.title.localeCompare(b.title);
        case 'created_at':
          return new Date(b.created_at).getTime() - new Date(a.created_at).getTime();
        case 'word_count':
          return (b.word_count || 0) - (a.word_count || 0);
        case 'updated_at':
        default:
          return new Date(b.updated_at).getTime() - new Date(a.updated_at).getTime();
      }
    });

    return displayDocs;
  };

  // Handle search
  const handleSearch = async () => {
    if (!searchQuery.trim()) {
      clearSearch();
      return;
    }

    await searchDocuments({
      query: searchQuery,
      document_types: filterBy !== 'all' ? [filterBy] : undefined,
      folder_ids: selectedFolder ? [selectedFolder] : undefined,
      series_ids: selectedSeries ? [selectedSeries] : undefined
    });
    setViewMode('search');
  };

  // Create new document
  const handleCreateDocument = async (templateId?: string) => {
    if (!newItemName.trim()) return;

    try {
      let newDoc: Document;
      if (templateId) {
        newDoc = await createFromTemplate(templateId, newItemName, selectedFolder || undefined);
      } else {
        newDoc = await createDocument(
          newItemName,
          filterBy !== 'all' ? filterBy : 'novel',
          selectedFolder || undefined,
          selectedSeries || undefined
        );
      }
      setShowCreateModal(false);
      setNewItemName('');
      onDocumentSelect(newDoc);
    } catch (error) {
      console.error('Failed to create document:', error);
    }
  };

  // Export document
  const handleExport = async (documentId: string, format: string) => {
    try {
      await exportDocument(documentId, format);
      setShowExportModal(false);
    } catch (error) {
      console.error('Export failed:', error);
    }
  };

  // Load analytics
  useEffect(() => {
    if (viewMode === 'analytics') {
      loadWritingStats('month');
    }
  }, [viewMode, loadWritingStats]);

  // Format file size
  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  // Format date
  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString();
  };

  // Get document icon
  const getDocumentIcon = (type?: string) => {
    switch (type) {
      case 'novel': return '📖';
      case 'chapter': return '📃';
      case 'character_sheet': return '👤';
      case 'outline': return '📋';
      case 'notes': return '📝';
      default: return '📄';
    }
  };

  return (
    <div className="document-manager-overlay">
      <div className="document-manager">
        {/* Header */}
        <div className="document-manager-header">
          <h2>📄 Document Manager</h2>
          <div className="header-actions">
            <div className="total-stats">
              {documents.length} docs • {getTotalWordCount().toLocaleString()} words
            </div>
            <button onClick={onClose} className="close-button">✕</button>
          </div>
        </div>

        {/* Navigation */}
        <div className="document-nav">
          <button 
            className={viewMode === 'documents' ? 'active' : ''}
            onClick={() => setViewMode('documents')}
          >
            📄 Documents
          </button>
          <button 
            className={viewMode === 'folders' ? 'active' : ''}
            onClick={() => setViewMode('folders')}
          >
            📁 Folders
          </button>
          <button 
            className={viewMode === 'series' ? 'active' : ''}
            onClick={() => setViewMode('series')}
          >
            📚 Series
          </button>
          <button 
            className={viewMode === 'templates' ? 'active' : ''}
            onClick={() => setViewMode('templates')}
          >
            📋 Templates
          </button>
          <button 
            className={viewMode === 'analytics' ? 'active' : ''}
            onClick={() => setViewMode('analytics')}
          >
            📊 Analytics
          </button>
        </div>

        {/* Search Bar */}
        <div className="search-section">
          <div className="search-input-group">
            <input
              type="text"
              placeholder="Search your writing..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
              className="search-input"
            />
            <button onClick={handleSearch} disabled={isSearching} className="search-button">
              {isSearching ? '⏳' : '🔍'}
            </button>
            {searchResults.length > 0 && (
              <button onClick={clearSearch} className="clear-search-button">✕</button>
            )}
          </div>
        </div>

        {/* Controls */}
        <div className="document-controls">
          <div className="controls-left">
            <select value={filterBy} onChange={(e) => setFilterBy(e.target.value as FilterBy)}>
              <option value="all">All Types</option>
              <option value="novel">📖 Novels</option>
              <option value="chapter">📃 Chapters</option>
              <option value="character_sheet">👤 Characters</option>
              <option value="outline">📋 Outlines</option>
              <option value="notes">📝 Notes</option>
            </select>
            <select value={sortBy} onChange={(e) => setSortBy(e.target.value as SortBy)}>
              <option value="updated_at">Recently Updated</option>
              <option value="created_at">Recently Created</option>
              <option value="title">Title A-Z</option>
              <option value="word_count">Word Count</option>
            </select>
          </div>
          <div className="controls-right">
            <button onClick={() => setShowCreateModal(true)} className="create-button">
              ➕ New Document
            </button>
            {viewMode === 'folders' && (
              <button onClick={() => setShowFolderModal(true)} className="create-button">
                📁 New Folder
              </button>
            )}
            {viewMode === 'series' && (
              <button onClick={() => setShowSeriesModal(true)} className="create-button">
                📚 New Series
              </button>
            )}
          </div>
        </div>

        {/* Content */}
        <div className="document-content">
          {error && (
            <div className="error-message">
              ⚠️ {error}
            </div>
          )}

          {/* Documents View */}
          {viewMode === 'documents' && (
            <div className="documents-grid">
              {/* Recent Documents */}
              <div className="recent-section">
                <h3>🕒 Recent Documents</h3>
                <div className="document-list">
                  {getRecentDocuments(5).map(doc => (
                    <div key={doc.id} className="document-item" onClick={() => onDocumentSelect(doc)}>
                      <div className="document-icon">{getDocumentIcon(doc.document_type)}</div>
                      <div className="document-info">
                        <div className="document-title">{doc.title}</div>
                        <div className="document-meta">
                          {(doc.word_count || 0).toLocaleString()} words • {formatDate(doc.updated_at)}
                        </div>
                      </div>
                      <div className="document-actions">
                        <button onClick={(e) => { e.stopPropagation(); setSelectedDocumentId(doc.id); setShowVersionModal(true); loadVersions(doc.id); }}>
                          📝 Versions
                        </button>
                        <button onClick={(e) => { e.stopPropagation(); setSelectedDocumentId(doc.id); setShowExportModal(true); }}>
                          📤 Export
                        </button>
                        <button onClick={(e) => { e.stopPropagation(); setSelectedDocumentId(doc.id); setShowShareModal(true); }}>
                          🔗 Share
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* All Documents */}
              <div className="all-documents-section">
                <h3>📄 All Documents ({getDisplayDocuments().length})</h3>
                <div className="document-list">
                  {getDisplayDocuments().map(doc => (
                    <div key={doc.id} className="document-item" onClick={() => onDocumentSelect(doc)}>
                      <div className="document-icon">{getDocumentIcon(doc.document_type)}</div>
                      <div className="document-info">
                        <div className="document-title">{doc.title}</div>
                        <div className="document-meta">
                          {(doc.word_count || 0).toLocaleString()} words • {formatDate(doc.updated_at)}
                          {doc.series_id && (
                            <span className="series-badge">
                              📚 {series.find(s => s.id === doc.series_id)?.name}
                            </span>
                          )}
                          {doc.folder_id && (
                            <span className="folder-badge">
                              📁 {folders.find(f => f.id === doc.folder_id)?.name}
                            </span>
                          )}
                        </div>
                      </div>
                      <div className="document-actions">
                        <button onClick={(e) => { e.stopPropagation(); duplicateDocument(doc.id); }}>
                          📋 Duplicate
                        </button>
                        <button onClick={(e) => { e.stopPropagation(); setSelectedDocumentId(doc.id); setShowVersionModal(true); loadVersions(doc.id); }}>
                          📝 Versions
                        </button>
                        <button onClick={(e) => { e.stopPropagation(); setSelectedDocumentId(doc.id); setShowExportModal(true); }}>
                          📤 Export
                        </button>
                        <button onClick={(e) => { e.stopPropagation(); deleteDocument(doc.id); }} className="delete-button">
                          🗑️ Delete
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}

          {/* Folders View */}
          {viewMode === 'folders' && (
            <div className="folders-grid">
              {getFolderTree().map(folder => (
                <div key={folder.id} className="folder-item" onClick={() => setSelectedFolder(folder.id)}>
                  <div className="folder-icon" style={{ color: folder.color }}>📁</div>
                  <div className="folder-info">
                    <div className="folder-name">{folder.name}</div>
                    <div className="folder-meta">
                      {getDocumentsByFolder(folder.id).length} documents
                    </div>
                  </div>
                  <div className="folder-actions">
                    <button onClick={(e) => { e.stopPropagation(); deleteFolder(folder.id); }} className="delete-button">
                      🗑️ Delete
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}

          {/* Series View */}
          {viewMode === 'series' && (
            <div className="series-grid">
              {series.map(seriesItem => (
                <div key={seriesItem.id} className="series-item" onClick={() => setSelectedSeries(seriesItem.id)}>
                  <div className="series-icon">📚</div>
                  <div className="series-info">
                    <div className="series-name">{seriesItem.name}</div>
                    <div className="series-meta">
                      {getDocumentsBySeries(seriesItem.id).length} documents • 
                      {seriesItem.total_word_count?.toLocaleString() || 0} words
                    </div>
                    {seriesItem.description && (
                      <div className="series-description">{seriesItem.description}</div>
                    )}
                  </div>
                  <div className="series-actions">
                    <button onClick={(e) => { e.stopPropagation(); deleteSeries(seriesItem.id); }} className="delete-button">
                      🗑️ Delete
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}

          {/* Templates View */}
          {viewMode === 'templates' && (
            <div className="templates-grid">
              {templates.map(template => (
                <div key={template.id} className="template-item">
                  <div className="template-icon">{getDocumentIcon(template.document_type)}</div>
                  <div className="template-info">
                    <div className="template-name">{template.name}</div>
                    <div className="template-preview">{template.preview_text}</div>
                  </div>
                  <div className="template-actions">
                    <button onClick={() => { setNewItemName(`New ${template.name}`); handleCreateDocument(template.id); }}>
                      ➕ Use Template
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}

          {/* Search Results */}
          {viewMode === 'search' && (
            <div className="search-results">
              <h3>🔍 Search Results ({searchResults.length})</h3>
              {searchResults.map(result => {
                const doc = documents.find(d => d.id === result.document_id);
                return (
                  <div key={result.document_id} className="search-result-item" onClick={() => doc && onDocumentSelect(doc)}>
                    <div className="result-title">{result.document_title}</div>
                    <div className="result-matches">
                      {result.matches.map((match, idx) => (
                        <div key={idx} className="result-match">
                          ...{match.context}...
                        </div>
                      ))}
                    </div>
                  </div>
                );
              })}
            </div>
          )}

          {/* Analytics View */}
          {viewMode === 'analytics' && (
            <div className="analytics-view">
              <div className="analytics-grid">
                <div className="stat-card">
                  <h4>📊 Writing Statistics</h4>
                  <div className="stat-value">{getTotalWordCount().toLocaleString()}</div>
                  <div className="stat-label">Total Words</div>
                </div>
                <div className="stat-card">
                  <h4>📄 Document Count</h4>
                  <div className="stat-value">{documents.length}</div>
                  <div className="stat-label">Total Documents</div>
                </div>
                <div className="stat-card">
                  <h4>📚 Series Count</h4>
                  <div className="stat-value">{series.length}</div>
                  <div className="stat-label">Active Series</div>
                </div>
                <div className="stat-card">
                  <h4>📁 Folders</h4>
                  <div className="stat-value">{folders.length}</div>
                  <div className="stat-label">Organized Folders</div>
                </div>
              </div>
              
              {writingStats && (
                <div className="writing-insights">
                  <h4>📈 Monthly Insights</h4>
                  <p>Average words per day: {Math.round(writingStats.avg_words_per_day || 0)}</p>
                  <p>Most productive day: {writingStats.most_productive_day || 'N/A'}</p>
                  <p>Total writing sessions: {writingStats.total_sessions || 0}</p>
                </div>
              )}
            </div>
          )}
        </div>

        {/* Modals */}
        {showCreateModal && (
          <div className="modal-overlay">
            <div className="modal">
              <h3>Create New Document</h3>
              <input
                type="text"
                placeholder="Document title..."
                value={newItemName}
                onChange={(e) => setNewItemName(e.target.value)}
                autoFocus
              />
              <div className="modal-actions">
                <button onClick={() => handleCreateDocument()} disabled={!newItemName.trim()}>
                  Create
                </button>
                <button onClick={() => { setShowCreateModal(false); setNewItemName(''); }}>
                  Cancel
                </button>
              </div>
            </div>
          </div>
        )}

        {showFolderModal && (
          <div className="modal-overlay">
            <div className="modal">
              <h3>Create New Folder</h3>
              <input
                type="text"
                placeholder="Folder name..."
                value={newItemName}
                onChange={(e) => setNewItemName(e.target.value)}
                autoFocus
              />
              <div className="modal-actions">
                <button onClick={async () => { 
                  await createFolder(newItemName); 
                  setShowFolderModal(false); 
                  setNewItemName(''); 
                }} disabled={!newItemName.trim()}>
                  Create
                </button>
                <button onClick={() => { setShowFolderModal(false); setNewItemName(''); }}>
                  Cancel
                </button>
              </div>
            </div>
          </div>
        )}

        {showSeriesModal && (
          <div className="modal-overlay">
            <div className="modal">
              <h3>Create New Series</h3>
              <input
                type="text"
                placeholder="Series name..."
                value={newItemName}
                onChange={(e) => setNewItemName(e.target.value)}
                autoFocus
              />
              <textarea
                placeholder="Series description (optional)..."
                value={newItemDescription}
                onChange={(e) => setNewItemDescription(e.target.value)}
              />
              <div className="modal-actions">
                <button onClick={async () => { 
                  await createSeries(newItemName, newItemDescription || undefined); 
                  setShowSeriesModal(false); 
                  setNewItemName(''); 
                  setNewItemDescription('');
                }} disabled={!newItemName.trim()}>
                  Create
                </button>
                <button onClick={() => { 
                  setShowSeriesModal(false); 
                  setNewItemName(''); 
                  setNewItemDescription('');
                }}>
                  Cancel
                </button>
              </div>
            </div>
          </div>
        )}

        {showExportModal && selectedDocumentId && (
          <div className="modal-overlay">
            <div className="modal">
              <h3>Export Document</h3>
              <div className="export-options">
                <button onClick={() => handleExport(selectedDocumentId, 'pdf')}>
                  📄 Export as PDF
                </button>
                <button onClick={() => handleExport(selectedDocumentId, 'docx')}>
                  📝 Export as DOCX
                </button>
                <button onClick={() => handleExport(selectedDocumentId, 'epub')}>
                  📖 Export as EPUB
                </button>
                <button onClick={() => handleExport(selectedDocumentId, 'txt')}>
                  📃 Export as TXT
                </button>
              </div>
              <div className="modal-actions">
                <button onClick={() => { setShowExportModal(false); setSelectedDocumentId(null); }}>
                  Cancel
                </button>
              </div>
            </div>
          </div>
        )}

        {showVersionModal && selectedDocumentId && (
          <div className="modal-overlay">
            <div className="modal version-modal">
              <h3>📝 Version History</h3>
              {isLoadingVersions ? (
                <div className="loading">Loading versions...</div>
              ) : (
                <div className="versions-list">
                  {versions.map(version => (
                    <div key={version.id} className="version-item">
                      <div className="version-info">
                        <div className="version-number">v{version.version_number}</div>
                        <div className="version-date">{formatDate(version.created_at)}</div>
                        <div className="version-words">{version.word_count?.toLocaleString()} words</div>
                        <div className="version-summary">{version.change_summary}</div>
                      </div>
                      <div className="version-actions">
                        <button onClick={() => restoreVersion(selectedDocumentId, version.id)}>
                          🔄 Restore
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              )}
              <div className="modal-actions">
                <button onClick={() => { setShowVersionModal(false); setSelectedDocumentId(null); }}>
                  Close
                </button>
              </div>
            </div>
          </div>
        )}

        {isLoading && (
          <div className="loading-overlay">
            <div className="loading-spinner">📄 Loading...</div>
          </div>
        )}
      </div>
    </div>
  );
};

export default DocumentManager; 