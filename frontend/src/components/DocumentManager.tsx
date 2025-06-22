import React, { useState } from 'react';
import { useDocuments } from '../hooks/useDocuments';
import { useAuth } from '../contexts/AuthContext';
import { Document } from '../services/api';
import {
  // Molecular Components
  DocumentManagerHeader,
  NavigationTabs,
  SearchBar,
  ControlsPanel,
  CreateModal,
  AuthPrompt,
  // Organism Components
  DocumentsView,
  FoldersView,
  TemplatesView,
  SearchResultsView,
  // Types
  ViewMode,
  SortBy,
  FilterBy
} from './document-manager';
import './DocumentManager.css';

interface DocumentManagerProps {
  onDocumentSelect: (document: Document) => void;
  onClose: () => void;
}

/**
 * Template/Page Component: Document Manager
 * 
 * CLEAN ARCHITECTURE IMPLEMENTATION:
 * - Single Responsibility: Coordinate document management workflow
 * - Delegates specific responsibilities to focused sub-components
 * - Uses Atomic Design principles (Atoms → Molecules → Organisms → Templates)
 * - Follows React composition patterns for maintainability
 * 
 * RESPONSIBILITIES:
 * 1. State coordination between sub-components
 * 2. Business logic orchestration
 * 3. Data flow management
 * 4. Error boundary handling
 */
const DocumentManager: React.FC<DocumentManagerProps> = ({ 
  onDocumentSelect, 
  onClose 
}) => {
  const { user } = useAuth();
  const {
    documents,
    folders,
    templates,
    searchResults,
    isLoading,
    error,
    createDocument,
    createFolder,
    deleteDocument,
    deleteFolder,
    duplicateDocument,
    searchDocuments,
    clearSearch,
    createFromTemplate,
    getDocumentsByFolder,
    getRecentDocuments,
    getTotalWordCount
  } = useDocuments();

  // State Management - Focused and minimal
  const [viewMode, setViewMode] = useState<ViewMode>('documents');
  const [selectedFolder, setSelectedFolder] = useState<string | null>(null);
  const [sortBy, setSortBy] = useState<SortBy>('updated_at');
  const [filterBy, setFilterBy] = useState<FilterBy>('all');
  const [searchQuery, setSearchQuery] = useState('');
  const [showCreateDocumentModal, setShowCreateDocumentModal] = useState(false);
  const [showCreateFolderModal, setShowCreateFolderModal] = useState(false);

  // Authentication Guard - Early return pattern
  if (!user) {
    return <AuthPrompt onClose={onClose} />;
  }

  // Business Logic - Document filtering and sorting
  const getDisplayDocuments = (): Document[] => {
    let displayDocs = documents;

    // Apply folder filter
    if (selectedFolder) {
      displayDocs = getDocumentsByFolder(selectedFolder);
    }

    // Apply type filter
    if (filterBy !== 'all') {
      displayDocs = displayDocs.filter(doc => doc.document_type === filterBy);
    }

    // Apply sorting
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

  // Event Handlers - Clean separation of concerns
  const handleSearch = async () => {
    if (!searchQuery.trim()) {
      clearSearch();
      return;
    }

    await searchDocuments({
      query: searchQuery,
      document_types: filterBy !== 'all' ? [filterBy] : undefined,
      folder_ids: selectedFolder ? [selectedFolder] : undefined
    });
    setViewMode('search');
  };

  const handleClearSearch = () => {
    clearSearch();
    setSearchQuery('');
    setViewMode('documents');
  };

  const handleCreateDocument = async (name: string) => {
    const newDoc = await createDocument(
      name,
      filterBy !== 'all' ? filterBy : 'novel',
      selectedFolder || undefined
    );
    setShowCreateDocumentModal(false);
    onDocumentSelect(newDoc);
  };

  const handleCreateFolder = async (name: string) => {
    await createFolder(name);
    setShowCreateFolderModal(false);
  };

  const handleUseTemplate = async (templateId: string, templateName: string) => {
    const newDoc = await createFromTemplate(
      templateId, 
      `New ${templateName}`, 
      selectedFolder || undefined
    );
    onDocumentSelect(newDoc);
  };

  const handleFolderSelect = (folderId: string) => {
    setSelectedFolder(folderId);
    setViewMode('documents');
  };

  // Content Rendering - Clean component composition
  const renderContent = () => {
    switch (viewMode) {
      case 'documents':
        return (
          <DocumentsView
            documents={getDisplayDocuments()}
            recentDocuments={getRecentDocuments()}
            folders={folders}
            onDocumentSelect={onDocumentSelect}
            onDuplicateDocument={duplicateDocument}
            onDeleteDocument={deleteDocument}
          />
        );

      case 'folders':
        return (
          <FoldersView
            folders={folders}
            getDocumentsByFolder={getDocumentsByFolder}
            onFolderSelect={handleFolderSelect}
            onDeleteFolder={deleteFolder}
          />
        );

      case 'templates':
        return (
          <TemplatesView
            templates={templates}
            onUseTemplate={handleUseTemplate}
          />
        );

      case 'search':
        return (
          <SearchResultsView
            searchResults={searchResults}
            documents={documents}
            onDocumentSelect={onDocumentSelect}
          />
        );

      default:
        return null;
    }
  };

  // Main Template Structure - Clean composition
  return (
    <div className="document-manager-overlay">
      <div className="document-manager">
        
        {/* Header Section */}
        <DocumentManagerHeader
          documentCount={documents.length}
          totalWordCount={getTotalWordCount()}
          onClose={onClose}
        />

        {/* Navigation Section */}
        <NavigationTabs
          viewMode={viewMode}
          onViewModeChange={setViewMode}
        />

        {/* Search Section */}
        <SearchBar
          searchQuery={searchQuery}
          onSearchChange={setSearchQuery}
          onSearch={handleSearch}
          onClearSearch={handleClearSearch}
          showClearButton={searchQuery !== '' || viewMode === 'search'}
        />

        {/* Controls Section */}
        <ControlsPanel
          sortBy={sortBy}
          filterBy={filterBy}
          viewMode={viewMode}
          onSortChange={setSortBy}
          onFilterChange={setFilterBy}
          onCreateDocument={() => setShowCreateDocumentModal(true)}
          onCreateFolder={() => setShowCreateFolderModal(true)}
        />

        {/* Content Section */}
        <div className="document-content">
          {error && (
            <div className="error-message">❌ {error}</div>
          )}
          {renderContent()}
        </div>

        {/* Modals */}
        <CreateModal
          isOpen={showCreateDocumentModal}
          title="Create New Document"
          placeholder="Document title..."
          onConfirm={handleCreateDocument}
          onCancel={() => setShowCreateDocumentModal(false)}
        />

        <CreateModal
          isOpen={showCreateFolderModal}
          title="Create New Folder"
          placeholder="Folder name..."
          onConfirm={handleCreateFolder}
          onCancel={() => setShowCreateFolderModal(false)}
        />

        {/* Loading Overlay */}
        {isLoading && (
          <div className="loading-overlay">
            <div className="loading-spinner"></div>
          </div>
        )}
      </div>
    </div>
  );
};

export default DocumentManager; 


