import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { DocumentThemeProvider } from './contexts/DocumentThemeContext';
import DocumentsPage from './pages/DocumentsPage';
import DocumentEditor from './pages/DocumentEditor';
import { WritingWorkspace } from './components/WritingWorkspace';
import { ErrorBoundary } from './components/ErrorBoundary';
import './App.css';
import './styles/light-theme.css';

// Main App Content
const AppContent: React.FC = () => {
  return (
      <div className="app-layout app-layout-mvp">
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
