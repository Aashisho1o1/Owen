import React from 'react';

interface SearchBarProps {
  searchQuery: string;
  onSearchChange: (query: string) => void;
  onSearch: () => void;
  onClearSearch: () => void;
  showClearButton: boolean;
  placeholder?: string;
}

/**
 * Atomic component: Search Bar
 * Single Responsibility: Handle search input and search actions
 */
export const SearchBar: React.FC<SearchBarProps> = ({
  searchQuery,
  onSearchChange,
  onSearch,
  onClearSearch,
  showClearButton,
  placeholder = "Search documents..."
}) => {
  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      onSearch();
    }
  };

  return (
    <div className="search-section">
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
    </div>
  );
}; 
 