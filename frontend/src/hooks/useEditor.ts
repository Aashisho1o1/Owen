import { useState, useCallback } from 'react';
import { logger } from '../utils/logger';

export interface UseEditorOptions {
  initialContent?: string;
}

export interface UseEditorReturn {
  editorContent: string;
  setEditorContent: React.Dispatch<React.SetStateAction<string>>;
  highlightedText: string | null;
  handleTextHighlighted: (text: string) => void;
  clearHighlightedText: () => void;
  updateContent: (newContent: string) => void;
}

const DEFAULT_INITIAL_CONTENT = 'Once upon a time, in a bustling city, a young detective named Kenji stumbled upon a mysterious diary. His partner, a seasoned veteran named Rina, always told him to trust his gut.';

export const useEditor = ({
  initialContent = DEFAULT_INITIAL_CONTENT,
}: UseEditorOptions = {}): UseEditorReturn => {
  const [editorContent, setEditorContent] = useState<string>(initialContent);
  const [highlightedText, setHighlightedText] = useState<string | null>(null);

  const handleTextHighlighted = useCallback((text: string) => {
    setHighlightedText(text);
    logger.log("Text Highlighted in useEditor:", { text });
    // Potentially, this could also trigger other actions, 
    // like passing the text to a chat context or an analysis service.
  }, []);

  const clearHighlightedText = useCallback(() => {
    setHighlightedText(null);
  }, []);

  const updateContent = useCallback((newContent: string) => {
    setEditorContent(newContent);
    logger.log("Editor content updated:", { 
      previousLength: editorContent.length, 
      newLength: newContent.length 
    });
    
    // Dispatch event to notify other components of content change
    window.dispatchEvent(new CustomEvent('editorContentUpdated', {
      detail: { newContent, timestamp: new Date().toISOString() }
    }));
  }, [editorContent.length]);

  return {
    editorContent,
    setEditorContent,
    highlightedText,
    handleTextHighlighted,
    clearHighlightedText,
    updateContent,
  };
}; 