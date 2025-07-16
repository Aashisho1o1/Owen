import React from 'react';
import { Document, DocumentFolder } from '../../services/api';
import { DocumentItem } from './DocumentItem';

interface DocumentsViewProps {
  documents: Document[];
  recentDocuments: Document[];
  folders: DocumentFolder[];
  onDocumentSelect: (document: Document) => void;
  onDuplicateDocument: (documentId: string) => void;
  onDeleteDocument: (documentId: string) => void;
}

/**
 * Organism component: Documents View
 * Single Responsibility: Display recent documents in a clean, organized layout
 */
export const DocumentsView: React.FC<DocumentsViewProps> = ({
  documents,
  recentDocuments,
  folders,
  onDocumentSelect,
  onDuplicateDocument,
  onDeleteDocument
}) => {
  return (
    <div className="documents-view-container">
      {/* Recent Documents Section - Full Width */}
      <div className="recent-documents-full">
        <h3>📝 Recent Documents</h3>
        <div className="document-list-grid">
          {recentDocuments.slice(0, 10).map(document => (
            <DocumentItem
              key={document.id}
              document={document}
              folders={folders}
              onSelect={onDocumentSelect}
              onDuplicate={onDuplicateDocument}
              onDelete={onDeleteDocument}
            />
          ))}
          {recentDocuments.length === 0 && (
            <div className="empty-state-large">
              <div className="empty-icon">📄</div>
              <h4>No recent documents yet</h4>
              <p>Create your first document to get started writing!</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}; 
 