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
    <div className="navigation-tabs">
      <button
        className={`nav-tab ${viewMode === 'documents' ? 'active' : ''}`}
        onClick={() => onViewModeChange('documents')}
      >
        📄 Documents
      </button>
      <button
        className={`nav-tab ${viewMode === 'folders' ? 'active' : ''}`}
        onClick={() => onViewModeChange('folders')}
      >
        📁 Folders
      </button>
      <button
        className={`nav-tab ${viewMode === 'appmap' ? 'active' : ''}`}
        onClick={() => onViewModeChange('appmap')}
      >
        🗺️ App Map
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
 