import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { DocumentThemeProvider } from './contexts/DocumentThemeContext';
import DocumentsPage from './pages/DocumentsPage';
import DocumentEditor from './pages/DocumentEditor';
import { WritingWorkspace } from './components/WritingWorkspace';
import { ErrorBoundary } from './components/ErrorBoundary';
import './App.css';

// Light theme overrides for MVP
const lightThemeOverrides = `
:root {
    --background-primary: #fefefe;
    --background-secondary: #f8f9fa;
    --background-tertiary: #ffffff;
    --text-primary: #2d3748;
    --text-secondary: #4a5568;
    --text-muted: #718096;
    --border-color: #e2e8f0;
    --accent-color: #3182ce;
    --accent-hover: #2c5aa0;
    --shadow-light: 0 1px 3px rgba(0, 0, 0, 0.1);
    --shadow-medium: 0 4px 6px rgba(0, 0, 0, 0.1);
  }
  
  body {
    background: var(--background-primary);
    color: var(--text-primary);
}

  .writing-workspace {
    background: var(--background-primary);
}

  .workspace-header {
    background: rgba(255, 255, 255, 0.95);
    backdrop-filter: blur(10px);
    border-bottom: 1px solid var(--border-color);
}

  .highlightable-editor {
    background: var(--background-tertiary);
    color: var(--text-primary);
  }
  
  .chat-panel {
    background: var(--background-secondary);
    border-left: 1px solid var(--border-color);
  }
`;

// Main App Content
const AppContent: React.FC = () => {
  return (
      <div className="app-layout app-layout-mvp">
        <style dangerouslySetInnerHTML={{ __html: lightThemeOverrides }} />
      <div className="app-main app-main-mvp">
        <Routes>
          <Route path="/" element={<WritingWorkspace />} />
          <Route path="/documents" element={<DocumentsPage />} />
            <Route path="/editor/:documentId" element={<DocumentEditor />} />
        </Routes>
        </div>
      </div>
  );
};

// Minimal App Component
const App: React.FC = () => {
  return (
    <Router>
      <ErrorBoundary>
        <DocumentThemeProvider>
          <AppContent />
        </DocumentThemeProvider>
      </ErrorBoundary>
    </Router>
  );
};

export default App;
