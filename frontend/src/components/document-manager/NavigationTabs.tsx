import React from 'react';
import { ViewMode } from './ControlsPanel';

interface NavigationTabsProps {
  viewMode: ViewMode;
  onViewModeChange: (mode: ViewMode) => void;
}

/**
 * Molecular component: Navigation Tabs
 * Single Responsibility: Handle view mode navigation
 */
export const NavigationTabs: React.FC<NavigationTabsProps> = ({
  viewMode,
  onViewModeChange
}) => {
  return (
    <div className="document-nav">
      <button 
        className={viewMode === 'documents' ? 'active' : ''}
        onClick={() => onViewModeChange('documents')}
      >
        📄 Documents
      </button>
      
      <button 
        className={viewMode === 'folders' ? 'active' : ''}
        onClick={() => onViewModeChange('folders')}
      >
        📁 Folders
      </button>
      
      {/* Templates tab removed - template system deprecated */}
      
      {viewMode === 'search' && (
        <button className="active">
          🔍 Search Results
        </button>
      )}
    </div>
  );
}; 
 