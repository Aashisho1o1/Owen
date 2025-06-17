import React, { createContext, useContext, useEffect, useState } from 'react';
import { DocumentTheme, DOCUMENT_THEMES } from '../constants/documentThemes';

interface DocumentThemeContextType {
  documentTheme: DocumentTheme | null;
  setDocumentTheme: (themeId: string | null) => void;
  applyDocumentTheme: (themeId: string) => void;
  clearDocumentTheme: () => void;
  isDocumentThemeActive: boolean;
}

const DocumentThemeContext = createContext<DocumentThemeContextType | undefined>(undefined);

export const useDocumentTheme = () => {
  const context = useContext(DocumentThemeContext);
  if (context === undefined) {
    throw new Error('useDocumentTheme must be used within a DocumentThemeProvider');
  }
  return context;
};

interface DocumentThemeProviderProps {
  children: React.ReactNode;
}

export const DocumentThemeProvider: React.FC<DocumentThemeProviderProps> = ({ children }) => {
  const [documentTheme, setDocumentThemeState] = useState<DocumentTheme | null>(null);
  const [isDocumentThemeActive, setIsDocumentThemeActive] = useState(false);

  // Apply document theme to CSS variables
  const applyThemeToDOM = (theme: DocumentTheme) => {
    const root = document.documentElement;
    
    // Apply typography
    root.style.setProperty('--doc-font-primary', theme.typography.primaryFont);
    root.style.setProperty('--doc-font-heading', theme.typography.headingFont);
    root.style.setProperty('--doc-font-accent', theme.typography.accentFont);
    root.style.setProperty('--doc-font-size-base', theme.typography.fontSize.base);
    root.style.setProperty('--doc-font-size-h1', theme.typography.fontSize.h1);
    root.style.setProperty('--doc-font-size-h2', theme.typography.fontSize.h2);
    root.style.setProperty('--doc-font-size-h3', theme.typography.fontSize.h3);
    root.style.setProperty('--doc-line-height', theme.typography.lineHeight);
    root.style.setProperty('--doc-letter-spacing', theme.typography.letterSpacing);
    
    // Apply colors
    root.style.setProperty('--doc-bg-primary', theme.colors.background);
    root.style.setProperty('--doc-bg-surface', theme.colors.surface);
    root.style.setProperty('--doc-color-primary', theme.colors.primary);
    root.style.setProperty('--doc-color-secondary', theme.colors.secondary);
    
    // Text colors
    root.style.setProperty('--doc-text-primary', theme.colors.text.primary);
    root.style.setProperty('--doc-text-secondary', theme.colors.text.secondary);
    root.style.setProperty('--doc-text-muted', theme.colors.text.muted);
    root.style.setProperty('--doc-text-accent', theme.colors.text.accent);
    
    // UI elements
    root.style.setProperty('--doc-border-color', theme.colors.border);
    root.style.setProperty('--doc-shadow-color', theme.colors.shadow);
    root.style.setProperty('--doc-selection-color', theme.colors.selection);
    root.style.setProperty('--doc-highlight-color', theme.colors.highlight);
    
    // Atmosphere
    if (theme.atmosphere.backgroundPattern) {
      root.style.setProperty('--doc-bg-pattern', theme.atmosphere.backgroundPattern);
    }
    root.style.setProperty('--doc-border-radius', theme.atmosphere.borderRadius);
    root.style.setProperty('--doc-shadow-subtle', theme.atmosphere.shadows.subtle);
    root.style.setProperty('--doc-shadow-medium', theme.atmosphere.shadows.medium);
    root.style.setProperty('--doc-shadow-dramatic', theme.atmosphere.shadows.dramatic);
    
    // Add theme class to body for additional styling
    document.body.classList.remove(...Array.from(document.body.classList).filter(c => c.startsWith('doc-theme-')));
    document.body.classList.add(`doc-theme-${theme.id}`);
  };

  // Clear document theme from DOM
  const clearThemeFromDOM = () => {
    const root = document.documentElement;
    const docProperties = [
      '--doc-font-primary', '--doc-font-heading', '--doc-font-accent',
      '--doc-font-size-base', '--doc-font-size-h1', '--doc-font-size-h2', '--doc-font-size-h3',
      '--doc-line-height', '--doc-letter-spacing',
      '--doc-bg-primary', '--doc-bg-surface', '--doc-color-primary', '--doc-color-secondary',
      '--doc-text-primary', '--doc-text-secondary', '--doc-text-muted', '--doc-text-accent',
      '--doc-border-color', '--doc-shadow-color', '--doc-selection-color', '--doc-highlight-color',
      '--doc-bg-pattern', '--doc-border-radius',
      '--doc-shadow-subtle', '--doc-shadow-medium', '--doc-shadow-dramatic'
    ];
    
    docProperties.forEach(prop => root.style.removeProperty(prop));
    
    // Remove theme classes
    document.body.classList.remove(...Array.from(document.body.classList).filter(c => c.startsWith('doc-theme-')));
  };

  const setDocumentTheme = (themeId: string | null) => {
    if (themeId && DOCUMENT_THEMES[themeId]) {
      const theme = DOCUMENT_THEMES[themeId];
      setDocumentThemeState(theme);
      setIsDocumentThemeActive(true);
    } else {
      setDocumentThemeState(null);
      setIsDocumentThemeActive(false);
    }
  };

  const applyDocumentTheme = (themeId: string) => {
    setDocumentTheme(themeId);
  };

  const clearDocumentTheme = () => {
    setDocumentTheme(null);
  };

  // Apply theme when it changes
  useEffect(() => {
    if (documentTheme && isDocumentThemeActive) {
      applyThemeToDOM(documentTheme);
    } else {
      clearThemeFromDOM();
    }
    
    // Cleanup on unmount
    return () => {
      if (!isDocumentThemeActive) {
        clearThemeFromDOM();
      }
    };
  }, [documentTheme, isDocumentThemeActive]);

  const value = {
    documentTheme,
    setDocumentTheme,
    applyDocumentTheme,
    clearDocumentTheme,
    isDocumentThemeActive,
  };

  return (
    <DocumentThemeContext.Provider value={value}>
      {children}
    </DocumentThemeContext.Provider>
  );
}; 