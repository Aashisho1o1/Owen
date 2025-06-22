import React from 'react';

export type SortBy = 'title' | 'updated_at' | 'created_at' | 'word_count';
export type FilterBy = 'all' | 'novel' | 'chapter' | 'character_sheet' | 'outline' | 'notes';
export type ViewMode = 'documents' | 'folders' | 'templates' | 'search';

interface ControlsPanelProps {
  sortBy: SortBy;
  filterBy: FilterBy;
  viewMode: ViewMode;
  onSortChange: (sort: SortBy) => void;
  onFilterChange: (filter: FilterBy) => void;
  onCreateDocument?: () => void;
  onCreateFolder?: () => void;
}

/**
 * Molecular component: Controls Panel
 * Single Responsibility: Handle document sorting, filtering, and creation controls
 */
export const ControlsPanel: React.FC<ControlsPanelProps> = ({
  sortBy,
  filterBy,
  viewMode,
  onSortChange,
  onFilterChange,
  onCreateDocument,
  onCreateFolder
}) => {
  return (
    <div className="document-controls">
      <div className="controls-left">
        <select 
          value={sortBy} 
          onChange={(e) => onSortChange(e.target.value as SortBy)}
        >
          <option value="updated_at">Sort by: Last Modified</option>
          <option value="created_at">Sort by: Created</option>
          <option value="title">Sort by: Title</option>
          <option value="word_count">Sort by: Word Count</option>
        </select>
        
        <select 
          value={filterBy} 
          onChange={(e) => onFilterChange(e.target.value as FilterBy)}
        >
          <option value="all">All Types</option>
          <option value="novel">Novels</option>
          <option value="chapter">Chapters</option>
          <option value="character_sheet">Characters</option>
          <option value="outline">Outlines</option>
          <option value="notes">Notes</option>
        </select>
      </div>
      
      <div className="controls-right">
        {viewMode === 'documents' && onCreateDocument && (
          <button onClick={onCreateDocument} className="create-button">
            ✨ New Document
          </button>
        )}
        {viewMode === 'folders' && onCreateFolder && (
          <button onClick={onCreateFolder} className="create-button">
            📁 New Folder
          </button>
        )}
      </div>
    </div>
  );
}; 
 