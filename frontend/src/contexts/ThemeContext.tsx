import React, { createContext, useContext, useEffect, useState } from 'react';

interface ThemeContextType {
  theme: 'light' | 'dark';
  toggleTheme: () => void;
  setTheme: (theme: 'light' | 'dark') => void;
}

const ThemeContext = createContext<ThemeContextType | undefined>(undefined);

export const useTheme = () => {
  const context = useContext(ThemeContext);
  if (context === undefined) {
    throw new Error('useTheme must be used within a ThemeProvider');
  }
  return context;
};

interface ThemeProviderProps {
  children: React.ReactNode;
}

export const ThemeProvider: React.FC<ThemeProviderProps> = ({ children }) => {
  // Initialize theme from localStorage or default to light
  const [theme, setThemeState] = useState<'light' | 'dark'>(() => {
    if (typeof window !== 'undefined') {
      const savedTheme = localStorage.getItem('owen-theme');
      if (savedTheme === 'light' || savedTheme === 'dark') {
        return savedTheme;
      }
      
      // Check system preference
      if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
        return 'dark';
      }
    }
    return 'light';
  });

  const setTheme = (newTheme: 'light' | 'dark') => {
    setThemeState(newTheme);
    localStorage.setItem('owen-theme', newTheme);
  };

  const toggleTheme = () => {
    setTheme(theme === 'light' ? 'dark' : 'light');
  };

  // Apply theme to document root
  useEffect(() => {
    const root = document.documentElement;
    
    // Remove existing theme classes
    root.classList.remove('theme-light', 'theme-dark');
    
    // Add new theme class
    root.classList.add(`theme-${theme}`);
    
    // Set CSS custom properties for the theme
    if (theme === 'dark') {
      // Dark theme variables
      root.style.setProperty('--bg-primary', '#0f172a');
      root.style.setProperty('--bg-secondary', '#1e293b');
      root.style.setProperty('--bg-tertiary', '#334155');
      root.style.setProperty('--bg-hover', '#475569');
      root.style.setProperty('--bg-active', '#64748b');
      
      root.style.setProperty('--text-primary', '#f8fafc');
      root.style.setProperty('--text-secondary', '#cbd5e1');
      root.style.setProperty('--text-muted', '#94a3b8');
      root.style.setProperty('--text-inverse', '#0f172a');
      
      root.style.setProperty('--border-primary', '#334155');
      root.style.setProperty('--border-secondary', '#475569');
      root.style.setProperty('--border-light', '#64748b');
      
      root.style.setProperty('--shadow-sm', '0 1px 2px 0 rgba(0, 0, 0, 0.3)');
      root.style.setProperty('--shadow-md', '0 4px 6px -1px rgba(0, 0, 0, 0.4)');
      root.style.setProperty('--shadow-lg', '0 10px 15px -3px rgba(0, 0, 0, 0.5)');
      
      root.style.setProperty('--accent-blue', '#3b82f6');
      root.style.setProperty('--accent-blue-hover', '#2563eb');
      root.style.setProperty('--accent-green', '#10b981');
      root.style.setProperty('--accent-green-hover', '#059669');
      root.style.setProperty('--accent-orange', '#f59e0b');
      root.style.setProperty('--accent-red', '#ef4444');
      
      root.style.setProperty('--editor-bg', '#1e293b');
      root.style.setProperty('--editor-content-bg', '#0f172a');
      root.style.setProperty('--chat-bg', '#1e293b');
      root.style.setProperty('--controls-bg', '#334155');
      
    } else {
      // Light theme variables
      root.style.setProperty('--bg-primary', '#ffffff');
      root.style.setProperty('--bg-secondary', '#f8fafc');
      root.style.setProperty('--bg-tertiary', '#f1f5f9');
      root.style.setProperty('--bg-hover', '#e2e8f0');
      root.style.setProperty('--bg-active', '#cbd5e1');
      
      root.style.setProperty('--text-primary', '#0f172a');
      root.style.setProperty('--text-secondary', '#475569');
      root.style.setProperty('--text-muted', '#64748b');
      root.style.setProperty('--text-inverse', '#ffffff');
      
      root.style.setProperty('--border-primary', '#e2e8f0');
      root.style.setProperty('--border-secondary', '#cbd5e1');
      root.style.setProperty('--border-light', '#f1f5f9');
      
      root.style.setProperty('--shadow-sm', '0 1px 2px 0 rgba(0, 0, 0, 0.05)');
      root.style.setProperty('--shadow-md', '0 4px 6px -1px rgba(0, 0, 0, 0.1)');
      root.style.setProperty('--shadow-lg', '0 10px 15px -3px rgba(0, 0, 0, 0.1)');
      
      root.style.setProperty('--accent-blue', '#3b82f6');
      root.style.setProperty('--accent-blue-hover', '#2563eb');
      root.style.setProperty('--accent-green', '#10b981');
      root.style.setProperty('--accent-green-hover', '#059669');
      root.style.setProperty('--accent-orange', '#f59e0b');
      root.style.setProperty('--accent-red', '#ef4444');
      
      root.style.setProperty('--editor-bg', '#ffffff');
      root.style.setProperty('--editor-content-bg', '#ffffff');
      root.style.setProperty('--chat-bg', '#f8fafc');
      root.style.setProperty('--controls-bg', '#ffffff');
    }
  }, [theme]);

  // Listen for system theme changes
  useEffect(() => {
    const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
    
    const handleSystemThemeChange = (e: MediaQueryListEvent) => {
      // Only apply system theme if user hasn't manually selected a theme
      const savedTheme = localStorage.getItem('owen-theme');
      if (!savedTheme) {
        setThemeState(e.matches ? 'dark' : 'light');
      }
    };

    mediaQuery.addEventListener('change', handleSystemThemeChange);
    
    return () => {
      mediaQuery.removeEventListener('change', handleSystemThemeChange);
    };
  }, []);

  const value = {
    theme,
    toggleTheme,
    setTheme,
  };

  return (
    <ThemeContext.Provider value={value}>
      {children}
    </ThemeContext.Provider>
  );
}; 