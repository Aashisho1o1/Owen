import React from 'react';
import { Document, DocumentFolder } from '../../services/api';
import { DocumentItem } from './DocumentItem';

interface DocumentsViewProps {
  documents: Document[];
  allDocuments: Document[];
  folders: DocumentFolder[];
  onDocumentSelect: (document: Document) => void;
  onDuplicateDocument: (documentId: string) => void;
  onDeleteDocument: (documentId: string) => void;
}

/**
 * Organism component: Documents View
 * Single Responsibility: Display all documents in a clean, organized layout
 */
export const DocumentsView: React.FC<DocumentsViewProps> = ({
  documents,
  allDocuments,
  folders,
  onDocumentSelect,
  onDuplicateDocument,
  onDeleteDocument
}) => {
  return (
    <div className="documents-view-container">
      <div className="document-list-grid">
        {allDocuments.map(document => (
          <DocumentItem
            key={document.id}
            document={document}
            folders={folders}
            onSelect={onDocumentSelect}
            onDuplicate={onDuplicateDocument}
            onDelete={onDeleteDocument}
          />
        ))}
        {allDocuments.length === 0 && (
          <div className="empty-state-large">
            <div className="empty-icon">📄</div>
            <h4>No documents yet</h4>
            <p>Create your first document to get started writing!</p>
          </div>
        )}
      </div>
    </div>
  );
}; 
 