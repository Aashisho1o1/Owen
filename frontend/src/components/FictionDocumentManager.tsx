import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import '../styles/FictionDocumentManager.css';
import apiClient from '../services/api/client';

// Types for fiction-specific documents
interface FictionDocument {
  id: string;
  title: string;
  content: string;
  document_type: 'novel' | 'chapter' | 'character_profile' | 'world_building' | 'plot_outline' | 'scene' | 'research_notes' | 'draft';
  status: 'draft' | 'in_progress' | 'first_draft' | 'revision' | 'final_draft' | 'published' | 'archived';
  word_count: number;
  word_count_target?: number;
  tags: string[];
  series_name?: string;
  chapter_number?: number;
  folder_id?: string;
  created_at: string;
  updated_at: string;
}

interface FictionFolder {
  id: string;
  name: string;
  folder_type: 'project' | 'series' | 'characters' | 'world_building' | 'research' | 'drafts' | 'general';
  color: string;
  description?: string;
  document_count?: number;
}

interface FictionTemplate {
  id: string;
  name: string;
  category: string;
  description: string;
  document_type: string;
  tags: string[];
}

interface FictionDocumentManagerProps {
  onDocumentSelect: (document: FictionDocument) => void;
  onClose: () => void;
}

export const FictionDocumentManager: React.FC<FictionDocumentManagerProps> = ({
  onDocumentSelect,
  onClose
}) => {
  const { user } = useAuth();
  const [documents, setDocuments] = useState<FictionDocument[]>([]);
  const [folders, setFolders] = useState<FictionFolder[]>([]);
  const [templates, setTemplates] = useState<FictionTemplate[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  
  // View state
  const [activeView, setActiveView] = useState<'documents' | 'folders' | 'templates'>('documents');
  const [selectedFolder, setSelectedFolder] = useState<string | null>(null);
  const [filterType, setFilterType] = useState<string>('all');
  const [searchQuery, setSearchQuery] = useState('');
  
  // Modal state
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [createType, setCreateType] = useState<'document' | 'folder'>('document');

  useEffect(() => {
    if (user) {
      loadData();
    }
  }, [user]);

  const loadData = async () => {
    try {
      setLoading(true);
      await Promise.all([
        loadDocuments(),
        loadFolders(),
        loadTemplates()
      ]);
    } catch (err) {
      setError('Failed to load data');
      console.error('Error loading data:', err);
    } finally {
      setLoading(false);
    }
  };

  const loadDocuments = async () => {
    try {
      const response = await apiClient.get('/api/documents');
      setDocuments(response.data.documents || []);
    } catch (err) {
      console.error('Error loading documents:', err);
      // Better error handling
      if (err instanceof Error) {
        setError(err.message);
      }
    }
  };

  const loadFolders = async () => {
    try {
      const response = await apiClient.get('/api/folders');
      setFolders(response.data || []);
    } catch (err) {
      console.error('Error loading folders:', err);
    }
  };

  const loadTemplates = async () => {
    try {
      const response = await apiClient.get('/api/fiction-templates');
      setTemplates(response.data || []);
    } catch (err) {
      console.error('Error loading templates:', err);
    }
  };

  const createDocument = async (title: string, documentType: string, templateId?: string) => {
    try {
      const payload = {
        title,
        document_type: documentType,
        template_id: templateId,
        folder_id: selectedFolder,
        content: '',
        tags: [],
        status: 'draft'
      };

      console.log('Creating document with payload:', payload);

      const response = await apiClient.post('/api/documents', payload);
      
      const newDoc = response.data;
      setDocuments(prev => [newDoc, ...prev]);
      onDocumentSelect(newDoc);
      setShowCreateModal(false);
    } catch (err) {
      console.error('Error creating document:', err);
      if (err instanceof Error) {
        setError(err.message);
      } else {
        setError('Failed to create document');
      }
    }
  };

  const createFromTemplate = async (templateId: string, title: string) => {
    try {
      const payload = {
        template_id: templateId,
        title,
        folder_id: selectedFolder,
        document_type: 'novel'
      };

      console.log('Creating from template with payload:', payload);

      const response = await apiClient.post('/api/documents/from-template', payload);
      
      const newDoc = response.data;
      setDocuments(prev => [newDoc, ...prev]);
      onDocumentSelect(newDoc);
    } catch (err) {
      console.error('Error creating from template:', err);
      if (err instanceof Error) {
        setError(err.message);
      } else {
        setError('Failed to create document from template');
      }
    }
  };

  const createFolder = async (name: string, folderType: string, color: string) => {
    try {
      const payload = {
        name,
        color
      };

      console.log('Creating folder with payload:', payload);

      const response = await apiClient.post('/api/folders', payload);
      
      const newFolder = response.data;
      setFolders(prev => [newFolder, ...prev]);
      setShowCreateModal(false);
    } catch (err) {
      console.error('Error creating folder:', err);
      if (err instanceof Error) {
        setError(err.message);
      } else {
        setError('Failed to create folder');
      }
    }
  };

  const filteredDocuments = documents.filter(doc => {
    if (selectedFolder && doc.folder_id !== selectedFolder) return false;
    if (filterType !== 'all' && doc.document_type !== filterType) return false;
    if (searchQuery && !doc.title.toLowerCase().includes(searchQuery.toLowerCase())) return false;
    return true;
  });

  const documentsByType = filteredDocuments.reduce((acc, doc) => {
    // Handle undefined/null document types
    const type = doc.document_type || 'draft';
    if (!acc[type]) acc[type] = [];
    acc[type].push(doc);
    return acc;
  }, {} as Record<string, FictionDocument[]>);

  const getDocumentIcon = (type: string) => {
    const icons = {
      novel: '📚',
      chapter: '📄',
      character_profile: '👤',
      world_building: '🌍',
      plot_outline: '📋',
      scene: '🎬',
      research_notes: '🔍',
      draft: '✏️'
    };
    return icons[type as keyof typeof icons] || '📄';
  };

  const getFolderIcon = (type: string) => {
    const icons = {
      project: '📁',
      series: '📚',
      characters: '👥',
      world_building: '🌍',
      research: '🔍',
      drafts: '✏️',
      general: '📂'
    };
    return icons[type as keyof typeof icons] || '📂';
  };

  if (!user) {
    return (
      <div className="fiction-doc-manager">
        <div className="auth-required">
          <h3>Sign in to access your documents</h3>
          <p>Create an account to start organizing your fiction writing projects.</p>
        </div>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="fiction-doc-manager">
        <div className="loading">
          <div className="spinner"></div>
          <p>Loading your writing projects...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="fiction-doc-manager">
      <div className="manager-header">
        <div className="header-left">
          <h2>Fiction Writing Manager</h2>
          <p>{documents.length} documents • {folders.length} folders</p>
        </div>
        <div className="header-right">
          {activeView === 'documents' && (
            <button className="btn-create" onClick={() => {
              setCreateType('document');
              setShowCreateModal(true);
            }}>
              ✨ New Document
            </button>
          )}
          {activeView === 'folders' && (
            <button className="btn-create" onClick={() => {
              setCreateType('folder');
              setShowCreateModal(true);
            }}>
              📁 New Folder
            </button>
          )}
          <button className="btn-close" onClick={onClose}>✕</button>
        </div>
      </div>

      <div className="manager-nav">
        <button 
          className={`nav-btn ${activeView === 'documents' ? 'active' : ''}`}
          onClick={() => setActiveView('documents')}
        >
          📄 Documents
        </button>
        <button 
          className={`nav-btn ${activeView === 'folders' ? 'active' : ''}`}
          onClick={() => setActiveView('folders')}
        >
          📁 Folders
        </button>
        <button 
          className={`nav-btn ${activeView === 'templates' ? 'active' : ''}`}
          onClick={() => setActiveView('templates')}
        >
          📋 Templates
        </button>
      </div>

      <div className="manager-controls">
        <div className="search-bar">
          <input
            type="text"
            placeholder="Search documents..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
        </div>
        
        {activeView === 'documents' && (
          <div className="filters">
            <select value={filterType} onChange={(e) => setFilterType(e.target.value)}>
              <option value="all">All Types</option>
              <option value="novel">Novels</option>
              <option value="chapter">Chapters</option>
              <option value="character_profile">Characters</option>
              <option value="world_building">World Building</option>
              <option value="plot_outline">Plot Outlines</option>
              <option value="scene">Scenes</option>
              <option value="research_notes">Research</option>
            </select>
          </div>
        )}
      </div>

      <div className="manager-content">
        {activeView === 'documents' && (
          <div className="documents-view">
            {Object.entries(documentsByType).map(([type, docs]) => (
              <div key={type} className="document-section">
                <h3>
                  {getDocumentIcon(type)} 
                  {type && typeof type === 'string' 
                    ? type.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase()) 
                    : 'Draft'
                  } 
                  ({docs.length})
                </h3>
                <div className="documents-grid">
                  {docs.map(doc => (
                    <div 
                      key={doc.id} 
                      className="document-card"
                      onClick={() => onDocumentSelect(doc)}
                    >
                      <div className="doc-header">
                        <span className="doc-icon">{getDocumentIcon(doc.document_type)}</span>
                        <span className="doc-status">{doc.status}</span>
                      </div>
                      <h4>{doc.title}</h4>
                      <div className="doc-meta">
                        <span>{doc.word_count} words</span>
                        {doc.word_count_target && (
                          <span>Goal: {doc.word_count_target}</span>
                        )}
                        {doc.series_name && (
                          <span>📚 {doc.series_name}</span>
                        )}
                        {doc.chapter_number && (
                          <span>Ch. {doc.chapter_number}</span>
                        )}
                      </div>
                      {doc.tags && doc.tags.length > 0 && (
                        <div className="doc-tags">
                          {doc.tags.slice(0, 3).map(tag => (
                            <span key={tag} className="tag">{tag}</span>
                          ))}
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>
        )}

        {activeView === 'folders' && (
          <div className="folders-view">
            <div className="folders-grid">
              {folders.map(folder => (
                <div 
                  key={folder.id} 
                  className="folder-card"
                  onClick={() => {
                    setSelectedFolder(folder.id);
                    setActiveView('documents');
                  }}
                >
                  <div className="folder-icon" style={{ color: folder.color }}>
                    {getFolderIcon(folder.folder_type)}
                  </div>
                  <h4>{folder.name}</h4>
                  <p>{folder.folder_type && typeof folder.folder_type === 'string' 
                    ? folder.folder_type.replace('_', ' ') 
                    : 'general'
                  }</p>
                  {folder.description && (
                    <p className="folder-desc">{folder.description}</p>
                  )}
                  <span className="doc-count">{folder.document_count || 0} documents</span>
                </div>
              ))}
            </div>
          </div>
        )}

        {activeView === 'templates' && (
          <div className="templates-view">
            {(() => {
              // Group templates by category with proper null/undefined handling
              const templatesByCategory = templates.reduce((acc, template) => {
                // Handle undefined/null categories
                const category = template.category || 'general';
                if (!acc[category]) acc[category] = [];
                acc[category].push(template);
                return acc;
              }, {} as Record<string, FictionTemplate[]>);

              // Render template sections
              return Object.entries(templatesByCategory).map(([category, categoryTemplates]) => (
                <div key={category} className="template-section">
                  <h3>
                    {category && typeof category === 'string' 
                      ? category.charAt(0).toUpperCase() + category.slice(1) 
                      : 'General'
                    } Templates
                  </h3>
                  <div className="templates-grid">
                    {categoryTemplates.map(template => (
                      <div 
                        key={template.id} 
                        className="template-card"
                        onClick={() => {
                          const title = prompt(`Enter title for new ${template.name}:`);
                          if (title) {
                            createFromTemplate(template.id, title);
                          }
                        }}
                      >
                        <div className="template-icon">
                          {getDocumentIcon(template.document_type)}
                        </div>
                        <h4>{template.name}</h4>
                        <p>{template.description}</p>
                        <div className="template-tags">
                          {template.tags && template.tags.length > 0 && 
                            template.tags.slice(0, 2).map(tag => (
                              <span key={tag} className="tag">{tag}</span>
                            ))
                          }
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              ));
            })()}
          </div>
        )}
      </div>

      {error && (
        <div className="error-message">
          <p>{error}</p>
          <button onClick={() => setError(null)}>✕</button>
        </div>
      )}

      {showCreateModal && createType === 'document' && (
        <CreateDocumentModal
          onClose={() => setShowCreateModal(false)}
          onCreate={createDocument}
          templates={templates}
        />
      )}

      {showCreateModal && createType === 'folder' && (
        <CreateFolderModal
          onClose={() => setShowCreateModal(false)}
          onCreate={createFolder}
        />
      )}
    </div>
  );
};

// Simple create document modal
interface CreateDocumentModalProps {
  onClose: () => void;
  onCreate: (title: string, type: string, templateId?: string) => void;
  templates: FictionTemplate[];
}

const CreateDocumentModal: React.FC<CreateDocumentModalProps> = ({
  onClose,
  onCreate,
  templates
}) => {
  const [title, setTitle] = useState('');
  const [documentType, setDocumentType] = useState('novel');
  const [selectedTemplate, setSelectedTemplate] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (title.trim()) {
      onCreate(title, documentType, selectedTemplate || undefined);
    }
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal" onClick={e => e.stopPropagation()}>
        <form onSubmit={handleSubmit}>
          <h3>Create New Document</h3>
          
          <div className="form-group">
            <label>Title</label>
            <input
              type="text"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder="Enter document title..."
              autoFocus
            />
          </div>

          <div className="form-group">
            <label>Document Type</label>
            <select value={documentType} onChange={(e) => setDocumentType(e.target.value)}>
              <option value="novel">Novel</option>
              <option value="chapter">Chapter</option>
              <option value="character_profile">Character Profile</option>
              <option value="world_building">World Building</option>
              <option value="plot_outline">Plot Outline</option>
              <option value="scene">Scene</option>
              <option value="research_notes">Research Notes</option>
              <option value="draft">Draft</option>
            </select>
          </div>

          <div className="form-group">
            <label>Template (Optional)</label>
            <select value={selectedTemplate} onChange={(e) => setSelectedTemplate(e.target.value)}>
              <option value="">No Template</option>
              {templates
                .filter(t => t.document_type === documentType)
                .map(template => (
                  <option key={template.id} value={template.id}>
                    {template.name}
                  </option>
                ))
              }
            </select>
          </div>

          <div className="modal-actions">
            <button type="button" onClick={onClose}>Cancel</button>
            <button type="submit" disabled={!title.trim()}>Create</button>
          </div>
        </form>
      </div>
    </div>
  );
};

// Create folder modal
interface CreateFolderModalProps {
  onClose: () => void;
  onCreate: (name: string, folderType: string, color: string) => void;
}

const CreateFolderModal: React.FC<CreateFolderModalProps> = ({
  onClose,
  onCreate
}) => {
  const [name, setName] = useState('');
  const [folderType, setFolderType] = useState('general');
  const [color, setColor] = useState('#3B82F6');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (name.trim()) {
      onCreate(name, folderType, color);
    }
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal" onClick={e => e.stopPropagation()}>
        <form onSubmit={handleSubmit}>
          <h3>Create New Folder</h3>
          
          <div className="form-group">
            <label>Folder Name</label>
            <input
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="Enter folder name..."
              autoFocus
            />
          </div>

          <div className="form-group">
            <label>Folder Type</label>
            <select value={folderType} onChange={(e) => setFolderType(e.target.value)}>
              <option value="general">General</option>
              <option value="project">Project</option>
              <option value="series">Series</option>
              <option value="characters">Characters</option>
              <option value="world_building">World Building</option>
              <option value="research">Research</option>
              <option value="drafts">Drafts</option>
            </select>
          </div>

          <div className="form-group">
            <label>Color</label>
            <input
              type="color"
              value={color}
              onChange={(e) => setColor(e.target.value)}
            />
          </div>

          <div className="modal-actions">
            <button type="button" onClick={onClose}>Cancel</button>
            <button type="submit" disabled={!name.trim()}>Create Folder</button>
          </div>
        </form>
      </div>
    </div>
  );
}; 