import React from 'react';
import { Document, DocumentFolder } from '../../services/api';
import { DocumentIcon } from './DocumentIcon';

interface DocumentItemProps {
  document: Document;
  folders: DocumentFolder[];
  onSelect: (document: Document) => void;
  onDuplicate: (documentId: string) => void;
  onDelete: (documentId: string) => void;
}

/**
 * Molecular component: Document Item
 * Single Responsibility: Display individual document with actions
 */
export const DocumentItem: React.FC<DocumentItemProps> = ({
  document,
  folders,
  onSelect,
  onDuplicate,
  onDelete
}) => {
  const formatDate = (dateString: string): string => {
    return new Date(dateString).toLocaleDateString();
  };

  const getFolderName = (folderId: string): string => {
    const folder = folders.find(f => f.id === folderId);
    return folder?.name || 'Unknown Folder';
  };

  const handleDuplicate = (e: React.MouseEvent) => {
    e.stopPropagation();
    onDuplicate(document.id);
  };

  const handleDelete = (e: React.MouseEvent) => {
    e.stopPropagation();
    onDelete(document.id);
  };

  return (
    <div 
      className="document-item" 
      onClick={() => onSelect(document)}
    >
      <DocumentIcon type={document.document_type} />
      
      <div className="document-info">
        <div className="document-title">{document.title}</div>
        <div className="document-meta">
          {document.word_count || 0} words • {formatDate(document.updated_at)}
          {document.folder_id && (
            <span className="folder-badge">
              📁 {getFolderName(document.folder_id)}
            </span>
          )}
        </div>
      </div>
      
      <div className="document-actions">
        <button onClick={handleDuplicate}>
          📋 Duplicate
        </button>
        <button onClick={handleDelete} className="delete-button">
          🗑️ Delete
        </button>
      </div>
    </div>
  );
}; 
 