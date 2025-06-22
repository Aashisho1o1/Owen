import React from 'react';
import { DocumentFolder } from '../../services/api';

interface FolderItemProps {
  folder: DocumentFolder;
  documentCount: number;
  onSelect: (folderId: string) => void;
  onDelete: (folderId: string) => void;
}

/**
 * Molecular component: Folder Item
 * Single Responsibility: Display individual folder with actions
 */
export const FolderItem: React.FC<FolderItemProps> = ({
  folder,
  documentCount,
  onSelect,
  onDelete
}) => {
  const handleDelete = (e: React.MouseEvent) => {
    e.stopPropagation();
    onDelete(folder.id);
  };

  return (
    <div 
      className="folder-item" 
      onClick={() => onSelect(folder.id)}
    >
      <div 
        className="folder-icon" 
        style={{ color: folder.color || '#3B82F6' }}
      >
        📁
      </div>
      
      <div className="folder-info">
        <div className="folder-name">{folder.name}</div>
        <div className="folder-meta">
          {documentCount} documents
        </div>
      </div>
      
      <div className="folder-actions">
        <button onClick={handleDelete} className="delete-button">
          🗑️
        </button>
      </div>
    </div>
  );
}; 
 