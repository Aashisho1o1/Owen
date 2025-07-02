/**
 * Unified Highlighting Service
 * Centralizes all highlighting logic to prevent conflicts and reduce complexity
 */

export interface HighlightRange {
  id: string;
  start: number;
  end: number;
  text: string;
  type: 'active' | 'feedback' | 'suggestion';
}

export class HighlightingService {
  private highlights: Map<string, HighlightRange> = new Map();
  private listeners: Set<(highlights: HighlightRange[]) => void> = new Set();

  /**
   * Add a highlight with deduplication
   */
  addHighlight(range: Omit<HighlightRange, 'id'>): string {
    const id = `highlight-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
    
    // Remove overlapping highlights of the same type
    this.removeOverlapping(range.start, range.end, range.type);
    
    const highlight: HighlightRange = { ...range, id };
    this.highlights.set(id, highlight);
    this.notifyListeners();
    
    return id;
  }

  /**
   * Remove a highlight by ID
   */
  removeHighlight(id: string): void {
    if (this.highlights.delete(id)) {
      this.notifyListeners();
    }
  }

  /**
   * Remove all highlights of a specific type
   */
  removeByType(type: HighlightRange['type']): void {
    let changed = false;
    for (const [id, highlight] of this.highlights) {
      if (highlight.type === type) {
        this.highlights.delete(id);
        changed = true;
      }
    }
    if (changed) {
      this.notifyListeners();
    }
  }

  /**
   * Clear all highlights
   */
  clearAll(): void {
    if (this.highlights.size > 0) {
      this.highlights.clear();
      this.notifyListeners();
    }
  }

  /**
   * Get all current highlights
   */
  getHighlights(): HighlightRange[] {
    return Array.from(this.highlights.values());
  }

  /**
   * Get highlights by type
   */
  getHighlightsByType(type: HighlightRange['type']): HighlightRange[] {
    return Array.from(this.highlights.values()).filter(h => h.type === type);
  }

  /**
   * Subscribe to highlight changes
   */
  subscribe(listener: (highlights: HighlightRange[]) => void): () => void {
    this.listeners.add(listener);
    // Send current state immediately
    listener(this.getHighlights());
    
    // Return unsubscribe function
    return () => this.listeners.delete(listener);
  }

  private removeOverlapping(start: number, end: number, type: HighlightRange['type']): void {
    for (const [id, highlight] of this.highlights) {
      if (highlight.type === type) {
        // Check for overlap
        if (!(end < highlight.start || start > highlight.end)) {
          this.highlights.delete(id);
        }
      }
    }
  }

  private notifyListeners(): void {
    const highlights = this.getHighlights();
    this.listeners.forEach(listener => {
      try {
        listener(highlights);
      } catch (error) {
        console.error('Error in highlight listener:', error);
      }
    });
  }
}

// Singleton instance
export const highlightingService = new HighlightingService();

// Helper hook for React components
import { useEffect, useState } from 'react';

export function useHighlights(type?: HighlightRange['type']) {
  const [highlights, setHighlights] = useState<HighlightRange[]>([]);

  useEffect(() => {
    const updateHighlights = (allHighlights: HighlightRange[]) => {
      if (type) {
        setHighlights(allHighlights.filter(h => h.type === type));
      } else {
        setHighlights(allHighlights);
      }
    };

    const unsubscribe = highlightingService.subscribe(updateHighlights);
    return unsubscribe;
  }, [type]);

  return highlights;
}
