import React from 'react';

interface SearchBarProps {
  searchQuery: string;
  onSearchChange: (query: string) => void;
  onSearch: () => void;
  onClearSearch: () => void;
  showClearButton: boolean;
  placeholder?: string;
  // Add controls props
  sortBy?: string;
  filterBy?: string;
  onSortChange?: (sort: string) => void;
  onFilterChange?: (filter: string) => void;
  // Add create button props
  viewMode?: string;
  onCreateDocument?: () => void;
  onCreateFolder?: () => void;
}

/**
 * Combined Search Bar and Controls
 * Single Responsibility: Handle search input and controls in horizontal layout
 */
export const SearchBar: React.FC<SearchBarProps> = ({
  searchQuery,
  onSearchChange,
  onSearch,
  onClearSearch,
  showClearButton,
  placeholder = "Search documents...",
  sortBy,
  filterBy,
  onSortChange,
  onFilterChange,
  viewMode,
  onCreateDocument,
  onCreateFolder
}) => {
  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      onSearch();
    }
  };

  return (
    <div className="search-and-controls-section">
      <div className="search-controls-horizontal">
        {/* Search Input */}
        <div className="search-input-group">
          <input
            type="text"
            className="search-input"
            placeholder={placeholder}
            value={searchQuery}
            onChange={(e) => onSearchChange(e.target.value)}
            onKeyPress={handleKeyPress}
          />
          <button onClick={onSearch} className="search-button">
            🔍
          </button>
          {showClearButton && (
            <button onClick={onClearSearch} className="clear-search-button">
              ✕
            </button>
          )}
        </div>

        {/* Controls */}
        <div className="controls-horizontal">
          {sortBy && onSortChange && (
            <select 
              value={sortBy} 
              onChange={(e) => onSortChange(e.target.value)}
              className="control-select"
            >
              <option value="updated_at">Sort by: Last Modified</option>
              <option value="created_at">Sort by: Created</option>
              <option value="title">Sort by: Title</option>
              <option value="word_count">Sort by: Word Count</option>
            </select>
          )}
          
          {filterBy && onFilterChange && (
            <select 
              value={filterBy} 
              onChange={(e) => onFilterChange(e.target.value)}
              className="control-select"
            >
              <option value="all">All Types</option>
              <option value="novel">Novels</option>
              <option value="chapter">Chapters</option>
              <option value="character_sheet">Characters</option>
              <option value="outline">Outlines</option>
              <option value="notes">Notes</option>
            </select>
          )}
          
          {/* Create Buttons */}
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
    </div>
  );
}; 
 