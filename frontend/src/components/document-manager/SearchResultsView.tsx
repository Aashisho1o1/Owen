import React from 'react';
import { Document, SearchResult } from '../../services/api';
import { DocumentIcon } from './DocumentIcon';

interface SearchResultsViewProps {
  searchResults: SearchResult[];
  documents: Document[];
  onDocumentSelect: (document: Document) => void;
}

/**
 * Organism component: Search Results View
 * Single Responsibility: Display and manage search results
 */
export const SearchResultsView: React.FC<SearchResultsViewProps> = ({
  searchResults,
  documents,
  onDocumentSelect
}) => {
  const formatDate = (dateString: string): string => {
    return new Date(dateString).toLocaleDateString();
  };

  return (
    <div className="search-results">
      <h3>🔍 Search Results ({searchResults.length})</h3>
      {searchResults.map(result => {
        const document = documents.find(d => d.id === result.document_id);
        
        if (!document) return null;

        return (
          <div 
            key={result.document_id} 
            className="search-result-item" 
            onClick={() => onDocumentSelect(document)}
          >
            <DocumentIcon type={document.document_type} />
            
            <div className="result-info">
              <div className="result-title">{result.document_title}</div>
              <div className="result-matches">
                {document.word_count || 0} words • {formatDate(document.updated_at)}
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );
}; 
 