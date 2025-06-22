import React from 'react';
import { DocumentFolder, Document } from '../../services/api';
import { FolderItem } from './FolderItem';

interface FoldersViewProps {
  folders: DocumentFolder[];
  getDocumentsByFolder: (folderId: string) => Document[];
  onFolderSelect: (folderId: string) => void;
  onDeleteFolder: (folderId: string) => void;
}

/**
 * Organism component: Folders View
 * Single Responsibility: Display and manage folder collection
 */
export const FoldersView: React.FC<FoldersViewProps> = ({
  folders,
  getDocumentsByFolder,
  onFolderSelect,
  onDeleteFolder
}) => {
  return (
    <div className="folders-grid">
      {folders.map(folder => (
        <FolderItem
          key={folder.id}
          folder={folder}
          documentCount={getDocumentsByFolder(folder.id).length}
          onSelect={onFolderSelect}
          onDelete={onDeleteFolder}
        />
      ))}
    </div>
  );
}; 
 