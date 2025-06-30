import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';

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
      const response = await fetch('/api/documents', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        setDocuments(data.documents || []);
      }
    } catch (err) {
      console.error('Error loading documents:', err);
    }
  };

  const loadFolders = async () => {
    try {
      const response = await fetch('/api/folders', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        setFolders(data || []);
      }
    } catch (err) {
      console.error('Error loading folders:', err);
    }
  };

  const loadTemplates = async () => {
    try {
      const response = await fetch('/api/fiction-templates');
      
      if (response.ok) {
        const data = await response.json();
        setTemplates(data || []);
      }
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

      const response = await fetch('/api/documents', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        },
        body: JSON.stringify(payload)
      });

      if (response.ok) {
        const newDoc = await response.json();
        setDocuments(prev => [newDoc, ...prev]);
        onDocumentSelect(newDoc);
        setShowCreateModal(false);
      }
    } catch (err) {
      console.error('Error creating document:', err);
      setError('Failed to create document');
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

      const response = await fetch('/api/documents/from-template', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        },
        body: JSON.stringify(payload)
      });

      if (response.ok) {
        const newDoc = await response.json();
        setDocuments(prev => [newDoc, ...prev]);
        onDocumentSelect(newDoc);
      }
    } catch (err) {
      console.error('Error creating from template:', err);
      setError('Failed to create document from template');
    }
  };

  const filteredDocuments = documents.filter(doc => {
    if (selectedFolder && doc.folder_id !== selectedFolder) return false;
    if (filterType !== 'all' && doc.document_type !== filterType) return false;
    if (searchQuery && !doc.title.toLowerCase().includes(searchQuery.toLowerCase())) return false;
    return true;
  });

  const documentsByType = filteredDocuments.reduce((acc, doc) => {
    const type = doc.document_type;
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
          <button className="btn-create" onClick={() => setShowCreateModal(true)}>
            ✨ New Document
          </button>
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
                  {type.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())} 
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
                      {doc.tags.length > 0 && (
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
                  <p>{folder.folder_type.replace('_', ' ')}</p>
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
            {templates.reduce((acc, template) => {
              if (!acc[template.category]) acc[template.category] = [];
              acc[template.category].push(template);
              return acc;
            }, {} as Record<string, FictionTemplate[]>).map ? 
              Object.entries(templates.reduce((acc, template) => {
                if (!acc[template.category]) acc[template.category] = [];
                acc[template.category].push(template);
                return acc;
              }, {} as Record<string, FictionTemplate[]>)).map(([category, categoryTemplates]) => (
                <div key={category} className="template-section">
                  <h3>{category.charAt(0).toUpperCase() + category.slice(1)} Templates</h3>
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
                          {template.tags.slice(0, 2).map(tag => (
                            <span key={tag} className="tag">{tag}</span>
                          ))}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )) : null
            }
          </div>
        )}
      </div>

      {error && (
        <div className="error-message">
          <p>{error}</p>
          <button onClick={() => setError(null)}>✕</button>
        </div>
      )}

      {showCreateModal && (
        <CreateDocumentModal
          onClose={() => setShowCreateModal(false)}
          onCreate={createDocument}
          templates={templates}
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