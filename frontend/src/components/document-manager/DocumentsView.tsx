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
 * Single Responsibility: Display and organize document lists (recent + all)
 */
export const DocumentsView: React.FC<DocumentsViewProps> = ({
  documents,
  recentDocuments,
  folders,
  onDocumentSelect,
  onDuplicateDocument,
  onDeleteDocument
}) => {
  const getDocumentStats = () => {
    const totalDocs = documents.length;
    const totalWords = documents.reduce((sum, doc) => sum + (doc.word_count || 0), 0);
    const recentCount = recentDocuments.length;
    const folderCount = folders.length;
    
    return { totalDocs, totalWords, recentCount, folderCount };
  };

  const { totalDocs, totalWords, recentCount, folderCount } = getDocumentStats();

  return (
    <div className="documents-view-container">
      {/* App Map Section - Quick Overview */}
      <div className="app-map-section">
        <h3>🗺️ Writing Dashboard</h3>
        <div className="app-map-grid">
          <div className="map-card">
            <div className="map-icon">📝</div>
            <div className="map-stats">
              <div className="map-number">{totalDocs}</div>
              <div className="map-label">Documents</div>
            </div>
          </div>
          <div className="map-card">
            <div className="map-icon">📊</div>
            <div className="map-stats">
              <div className="map-number">{totalWords.toLocaleString()}</div>
              <div className="map-label">Total Words</div>
            </div>
          </div>
          <div className="map-card">
            <div className="map-icon">⏰</div>
            <div className="map-stats">
              <div className="map-number">{recentCount}</div>
              <div className="map-label">Recent</div>
            </div>
          </div>
          <div className="map-card">
            <div className="map-icon">📁</div>
            <div className="map-stats">
              <div className="map-number">{folderCount}</div>
              <div className="map-label">Folders</div>
            </div>
          </div>
        </div>
      </div>

      {/* Documents Content Grid */}
      <div className="documents-content-grid">
        {/* Recent Documents Section */}
        <div className="recent-section">
          <h3>📝 Recent Documents</h3>
          <div className="document-list">
            {recentDocuments.slice(0, 5).map(document => (
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
              <div className="empty-state-small">
                <p>No recent documents yet. Create your first document to get started!</p>
              </div>
            )}
          </div>
        </div>

        {/* All Documents Section */}
        <div className="all-documents-section">
          <h3>📚 All Documents</h3>
          <div className="document-list">
            {documents.map(document => (
              <DocumentItem
                key={document.id}
                document={document}
                folders={folders}
                onSelect={onDocumentSelect}
                onDuplicate={onDuplicateDocument}
                onDelete={onDeleteDocument}
              />
            ))}
            {documents.length === 0 && (
              <div className="empty-state-small">
                <p>No documents found. Start writing your first story!</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}; 
 