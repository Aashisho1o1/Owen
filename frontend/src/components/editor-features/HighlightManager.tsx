import React, { useCallback, useState } from 'react';
import { HighlightInfo } from './CustomHighlightExtension';

interface HighlightManagerProps {
  children: (props: {
    highlights: HighlightInfo[];
    createHighlight: (text: string, color: string, position: { from: number; to: number }) => string;
    removeHighlight: (highlightId: string) => void;
    clearAllHighlights: () => void;
  }) => React.ReactNode;
}

/**
 * Container Component: Highlight Manager
 * Single Responsibility: Manage highlight state and operations
 * Uses render props pattern for maximum flexibility
 */
export const HighlightManager: React.FC<HighlightManagerProps> = ({ children }) => {
  const [highlights, setHighlights] = useState<HighlightInfo[]>([]);

  const createHighlight = useCallback((text: string, color: string, position: { from: number; to: number }): string => {
    const highlightId = `highlight-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
    
    const highlightInfo: HighlightInfo = {
      id: highlightId,
      text,
      color,
      position,
      timestamp: Date.now(),
    };

    setHighlights(prev => [...prev, highlightInfo]);
    return highlightId;
  }, []);

  const removeHighlight = useCallback((highlightId: string) => {
    setHighlights(prev => prev.filter(h => h.id !== highlightId));
  }, []);

  const clearAllHighlights = useCallback(() => {
    setHighlights([]);
  }, []);

  return (
    <>
      {children({
        highlights,
        createHighlight,
        removeHighlight,
        clearAllHighlights
      })}
    </>
  );
};
