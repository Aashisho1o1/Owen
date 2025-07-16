import React from 'react';

/**
 * Organism component: App Map View
 * Single Responsibility: Display user guide and navigation help for the application
 */
export const AppMapView: React.FC = () => {
  return (
    <div className="app-map-view">
      <div className="app-map-header">
        <h2>🗺️ App Map - How to Navigate This App</h2>
        <p>Your guide to using the writing workspace effectively</p>
        <div className="detailed-guide-link">
          <a 
            href="https://drive.google.com/file/d/1ab8nrRNUbZNAYsMThGVp9we3CapHMjfB/view?usp=sharing" 
            target="_blank" 
            rel="noopener noreferrer"
            className="guide-link"
          >
            📖 Click here for further details on navigating this app
          </a>
        </div>
      </div>

      <div className="app-map-content">
        <div className="guide-section">
          <h3>📄 Documents Section</h3>
          <ul>
            <li><strong>Create Documents:</strong> Click "Create Document" to start a new piece</li>
            <li><strong>Document Types:</strong> Choose from Novel, Chapter, Character Sheet, Outline, or Notes</li>
            <li><strong>Sort & Filter:</strong> Use the controls to organize your documents by title, date, or word count</li>
            <li><strong>Quick Actions:</strong> Duplicate or delete documents using the action buttons</li>
          </ul>
        </div>

        <div className="guide-section">
          <h3>📁 Folders Section</h3>
          <ul>
            <li><strong>Organize:</strong> Create folders to group related documents</li>
            <li><strong>Manage:</strong> Rename or delete folders as needed</li>
            <li><strong>Navigation:</strong> Click on folders to view their contents</li>
          </ul>
        </div>

        <div className="guide-section">
          <h3>✍️ Writing Workspace</h3>
          <ul>
            <li><strong>Rich Editor:</strong> Full-featured text editor with formatting options</li>
            <li><strong>AI Chat:</strong> Get writing assistance and feedback in the chat panel</li>
            <li><strong>Highlighting:</strong> Select text to highlight and get contextual suggestions</li>
            <li><strong>Auto-save:</strong> Your work is automatically saved as you type</li>
          </ul>
        </div>

        <div className="guide-section">
          <h3>🤖 AI Features</h3>
          <ul>
            <li><strong>Chat Assistant:</strong> Ask questions about your writing or get creative suggestions</li>
            <li><strong>Grammar Check:</strong> Get real-time grammar and style feedback</li>
            <li><strong>Character Voice:</strong> Generate character-specific dialogue and responses</li>
            <li><strong>Story Generation:</strong> Get help with plot development and story structure</li>
          </ul>
        </div>

        <div className="guide-section">
          <h3>🔍 Search & Discovery</h3>
          <ul>
            <li><strong>Search Documents:</strong> Find documents by title, content, or type</li>
            <li><strong>Filter Results:</strong> Narrow down results by document type</li>
            <li><strong>Quick Access:</strong> Recent documents are prioritized in results</li>
          </ul>
        </div>

        <div className="guide-section">
          <h3>⚡ Pro Tips</h3>
          <ul>
            <li><strong>Keyboard Shortcuts:</strong> Use Ctrl+S to save, Ctrl+Z to undo</li>
            <li><strong>Themes:</strong> Switch between light and dark themes for comfortable writing</li>
            <li><strong>Focus Mode:</strong> Minimize distractions by hiding the chat panel when writing</li>
            <li><strong>Document Themes:</strong> Choose different themes for different document types</li>
          </ul>
        </div>
      </div>
    </div>
  );
}; 