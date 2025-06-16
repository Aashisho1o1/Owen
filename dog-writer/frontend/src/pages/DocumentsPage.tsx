import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useDocuments } from '../hooks/useDocuments';
import { Document } from '../services/api';
import './DocumentsPage.css';

interface FictionTemplate {
  id: string;
  name: string;
  genre: string;
  description: string;
  icon: string;
  content: string;
  color: string;
}

const FICTION_TEMPLATES: FictionTemplate[] = [
  {
    id: 'romance',
    name: 'Romance Novel',
    genre: 'Romance',
    description: 'A template for romantic fiction with character development arcs',
    icon: '💕',
    color: '#ff6b9d',
    content: `# Romance Novel Template

## Main Characters
### Protagonist
- Name:
- Age:
- Occupation:
- Background:
- Personality traits:
- Internal conflict:

### Love Interest
- Name:
- Age:
- Occupation:
- Background:
- Personality traits:
- What makes them attractive:

## Plot Structure
### Meet-Cute (Chapter 1-2)
- How do they first encounter each other?
- What's the initial impression?
- What sparks their interest?

### Building Tension (Chapter 3-8)
- Obstacles to their relationship:
- Moments of connection:
- Misunderstandings:

### The Crisis (Chapter 9-10)
- What threatens to keep them apart?
- Dark moment:

### Resolution (Chapter 11-12)
- How do they overcome obstacles?
- The declaration of love:
- Happy ending:

## Chapter Outline
1. Chapter 1: [Title] - [Brief description]
2. Chapter 2: [Title] - [Brief description]
...

## Key Themes
- 
- 
- 

## Setting
- Time period:
- Location:
- Atmosphere:
`
  },
  {
    id: 'thriller',
    name: 'Thriller Novel',
    genre: 'Thriller',
    description: 'A template for suspenseful thrillers and mysteries',
    icon: '🔍',
    color: '#4c566a',
    content: `# Thriller Novel Template

## Main Characters
### Protagonist
- Name:
- Profession:
- Special skills:
- Personal stakes:
- Fatal flaw:

### Antagonist
- Name:
- Motivation:
- Methods:
- Resources:
- Connection to protagonist:

## Plot Structure
### The Hook (Chapter 1)
- Inciting incident:
- What grabs the reader immediately?

### Rising Action (Chapters 2-8)
- Clues discovered:
- Red herrings:
- Escalating danger:
- Plot twists:

### Climax (Chapters 9-10)
- Final confrontation:
- Revelation of truth:

### Resolution (Chapter 11)
- Aftermath:
- Justice served:

## Mystery Elements
- Central mystery:
- Key clues:
- False leads:
- Final revelation:

## Suspense Techniques
- Ticking clock:
- Information gaps:
- Foreshadowing:
- Cliffhangers:

## Chapter Outline
1. Chapter 1: [Title] - [The hook]
2. Chapter 2: [Title] - [First clue]
...
`
  },
  {
    id: 'fantasy',
    name: 'Fantasy Epic',
    genre: 'Fantasy',
    description: 'A template for epic fantasy adventures',
    icon: '🐉',
    color: '#8b5a3c',
    content: `# Fantasy Epic Template

## World Building
### Magic System
- How magic works:
- Rules and limitations:
- Who can use magic:
- Cost of magic:

### Geography
- Main kingdoms/regions:
- Important locations:
- Climate and terrain:

### Cultures
- Major races/peoples:
- Languages:
- Customs and beliefs:
- Political structures:

## Main Characters
### Hero/Heroine
- Name:
- Background:
- Special abilities:
- Quest/goal:
- Character arc:

### Supporting Characters
- Mentor:
- Allies:
- Love interest:
- Companions:

### Villain
- Name:
- Motivation:
- Powers:
- Army/followers:

## The Quest
### Call to Adventure
- What forces the hero to act?
- Initial refusal:
- Crossing the threshold:

### Trials and Challenges
- Tests of character:
- Allies gained:
- Enemies faced:
- Magical items acquired:

### Final Battle
- Ultimate confrontation:
- Sacrifice required:
- Victory and transformation:

## Chapter Outline
1. Chapter 1: [Title] - [Ordinary world]
2. Chapter 2: [Title] - [Call to adventure]
...
`
  },
  {
    id: 'scifi',
    name: 'Science Fiction',
    genre: 'Sci-Fi',
    description: 'A template for futuristic science fiction stories',
    icon: '🚀',
    color: '#5e81ac',
    content: `# Science Fiction Template

## Setting
### Time Period
- Year/era:
- Technological level:
- Social changes:

### World State
- Political structure:
- Environmental conditions:
- Key locations:

## Technology
### Core Technology
- Central innovation:
- How it works:
- Impact on society:
- Potential dangers:

### Other Technologies
- Transportation:
- Communication:
- Medical advances:
- Weapons:

## Characters
### Protagonist
- Name:
- Role in society:
- Relationship to technology:
- Personal goals:

### Supporting Cast
- Scientists:
- Politicians:
- Rebels:
- AI characters:

## Central Conflict
### The Problem
- Technological dilemma:
- Ethical questions:
- Societal issues:

### Stakes
- Personal consequences:
- Global/universal impact:
- Moral implications:

## Plot Structure
### Setup (Chapters 1-3)
- World introduction:
- Character establishment:
- Problem revelation:

### Development (Chapters 4-8)
- Investigation/exploration:
- Complications arise:
- Allies and enemies:

### Climax (Chapters 9-10)
- Final confrontation:
- Technology's role:
- Resolution of conflict:

## Chapter Outline
1. Chapter 1: [Title] - [World introduction]
2. Chapter 2: [Title] - [Character focus]
...
`
  },
  {
    id: 'historical',
    name: 'Historical Fiction',
    genre: 'Historical',
    description: 'A template for historically-based narratives',
    icon: '📚',
    color: '#d08770',
    content: `# Historical Fiction Template

## Historical Setting
### Time Period
- Specific years:
- Major historical events:
- Social context:

### Location
- Geographic setting:
- Important places:
- Local customs:

## Historical Research
### Key Events
- Major happenings of the era:
- How they affect your story:
- Timeline of events:

### Daily Life
- How people lived:
- Technology available:
- Social hierarchies:
- Cultural norms:

## Characters
### Main Character
- Name:
- Social class:
- Occupation:
- Personal goals:
- How history affects them:

### Historical Figures
- Real people included:
- Their role in your story:
- Historical accuracy:

## Plot Integration
### Historical Events as Plot Points
- Which events drive the story:
- Personal vs. historical stakes:
- Accuracy vs. artistic license:

### Themes
- Universal human experiences:
- Historical lessons:
- Contemporary relevance:

## Chapter Outline
1. Chapter 1: [Title] - [Historical setup]
2. Chapter 2: [Title] - [Character introduction]
...

## Research Notes
- Primary sources consulted:
- Historical details to verify:
- Expert consultations:
`
  },
  {
    id: 'biography',
    name: 'Biography/Memoir',
    genre: 'Biography',
    description: 'A template for life stories and memoirs',
    icon: '👤',
    color: '#a3be8c',
    content: `# Biography/Memoir Template

## Subject Information
### Basic Details
- Full name:
- Birth date and place:
- Death date (if applicable):
- Nationality:
- Known for:

### Early Life
- Family background:
- Childhood experiences:
- Education:
- Formative events:

## Life Structure
### Major Periods
1. Childhood and youth:
2. Early career/adult life:
3. Peak achievements:
4. Later years:
5. Legacy:

### Key Relationships
- Family members:
- Mentors:
- Collaborators:
- Rivals:
- Loved ones:

## Achievements and Challenges
### Major Accomplishments
- Professional achievements:
- Personal milestones:
- Impact on others:
- Historical significance:

### Obstacles Overcome
- Personal struggles:
- Professional setbacks:
- Health challenges:
- Social barriers:

## Themes
### Personal Growth
- Character development:
- Lessons learned:
- Values demonstrated:

### Historical Context
- Era they lived in:
- Social/political climate:
- Cultural influences:

## Chapter Structure
1. Chapter 1: [Early years]
2. Chapter 2: [Formative experiences]
3. Chapter 3: [First major achievement]
...

## Sources and Research
- Primary sources:
- Interviews conducted:
- Documents reviewed:
- Photos/artifacts:
`
  },
  {
    id: 'comedy',
    name: 'Comedy Novel',
    genre: 'Comedy',
    description: 'A template for humorous fiction',
    icon: '😄',
    color: '#ebcb8b',
    content: `# Comedy Novel Template

## Humor Style
### Type of Comedy
- Situational comedy:
- Character-driven humor:
- Satirical elements:
- Absurdist elements:
- Romantic comedy:

### Target Audience
- Age group:
- Cultural background:
- Humor preferences:

## Main Characters
### Comic Protagonist
- Name:
- Comedic flaw:
- What makes them funny:
- Character arc:
- Relatability factor:

### Supporting Cast
- Straight man/woman:
- Comic relief characters:
- Antagonist (if applicable):
- Love interest:

## Plot Structure
### Setup (Chapters 1-3)
- Normal world:
- Comedic premise:
- Initial situation:

### Escalation (Chapters 4-8)
- Complications multiply:
- Misunderstandings grow:
- Stakes increase:
- Running gags develop:

### Climax (Chapters 9-10)
- Everything goes wrong:
- Maximum chaos:
- Truth revealed:

### Resolution (Chapter 11)
- Problems resolved:
- Lessons learned:
- Happy ending:

## Comedy Techniques
### Running Gags
- Recurring jokes:
- Character quirks:
- Situational repeats:

### Comedic Timing
- Setup and payoff:
- Rule of three:
- Unexpected turns:

## Chapter Outline
1. Chapter 1: [Title] - [Setup]
2. Chapter 2: [Title] - [First complication]
...

## Humor Notes
- Funny dialogue examples:
- Physical comedy moments:
- Satirical targets:
`
  }
];

const DocumentsPage: React.FC = () => {
  const navigate = useNavigate();
  const { 
    documents, 
    isLoading, 
    error, 
    createDocument, 
    deleteDocument, 
    updateDocument,
    getRecentDocuments,
    refreshAll 
  } = useDocuments();
  
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

  const handleCreateFromTemplate = async (template: FictionTemplate) => {
    try {
      const newDoc = await createDocument(
        `New ${template.genre} Novel`,
        'novel',
        undefined,
        undefined
      );
      
      // Update the document with template content
      await updateDocument(newDoc.id, { content: template.content });
      
      // Navigate to the editor with the new document
      navigate(`/editor/${newDoc.id}`);
    } catch (error) {
      console.error('Failed to create document from template:', error);
    }
  };

  const handleCreateBlankDocument = async () => {
    try {
      const newDoc = await createDocument('Untitled Document', 'novel');
      navigate(`/editor/${newDoc.id}`);
    } catch (error) {
      console.error('Failed to create blank document:', error);
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

            {/* Fiction Templates */}
            {FICTION_TEMPLATES.map((template) => (
              <div 
                key={template.id}
                className="template-card"
                onClick={() => handleCreateFromTemplate(template)}
                style={{ '--template-color': template.color } as React.CSSProperties}
              >
                <div className="template-preview">
                  <div className="template-icon">{template.icon}</div>
                  <div className="template-content">
                    <h4>{template.name}</h4>
                    <p>{template.description}</p>
                  </div>
                </div>
                <h3>{template.name}</h3>
                <span className="template-genre">{template.genre}</span>
              </div>
            ))}
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

        {sortedDocuments.length === 0 && !isLoading && (
          <div className="empty-state">
            <div className="empty-icon">📝</div>
            <h3>No documents found</h3>
            <p>
              {searchTerm 
                ? `No documents match "${searchTerm}"`
                : "You haven't created any documents yet. Start writing by choosing a template above!"
              }
            </p>
          </div>
        )}
      </div>

      {showDeleteModal && (
        <div className="modal-overlay">
          <div className="delete-modal">
            <h3>Delete Documents</h3>
            <p>
              Are you sure you want to delete {selectedDocuments.size} document(s)? 
              This action cannot be undone.
            </p>
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

      {error && (
        <div className="error-message">
          {error}
        </div>
      )}
    </div>
  );
};

export default DocumentsPage;