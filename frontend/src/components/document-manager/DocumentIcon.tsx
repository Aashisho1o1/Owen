import React from 'react';

interface DocumentIconProps {
  type?: string;
  className?: string;
}

/**
 * Atomic component: Document Icon
 * Single Responsibility: Display appropriate icon based on document type
 */
export const DocumentIcon: React.FC<DocumentIconProps> = ({ type, className = '' }) => {
  const getDocumentIcon = (documentType?: string): string => {
    switch (documentType) {
      case 'novel': return '📖';
      case 'chapter': return '📃';
      case 'character_sheet': return '👤';
      case 'outline': return '📋';
      case 'notes': return '📝';
      default: return '📄';
    }
  };

  return (
    <div className={`document-icon ${className}`}>
      {getDocumentIcon(type)}
    </div>
  );
}; 
 