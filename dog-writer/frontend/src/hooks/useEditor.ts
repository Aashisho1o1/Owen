import { useState, useCallback } from 'react';

export interface UseEditorOptions {
  initialContent?: string;
}

export interface UseEditorReturn {
  editorContent: string;
  setEditorContent: React.Dispatch<React.SetStateAction<string>>;
  highlightedText: string | null;
  handleTextHighlighted: (text: string) => void;
  clearHighlightedText: () => void;
}

const DEFAULT_INITIAL_CONTENT = 'Once upon a time, in a bustling city, a young detective named Kenji stumbled upon a mysterious diary. His partner, a seasoned veteran named Rina, always told him to trust his gut.';

export const useEditor = ({
  initialContent = DEFAULT_INITIAL_CONTENT,
}: UseEditorOptions = {}): UseEditorReturn => {
  const [editorContent, setEditorContent] = useState<string>(initialContent);
  const [highlightedText, setHighlightedText] = useState<string | null>(null);

  const handleTextHighlighted = useCallback((text: string) => {
    setHighlightedText(text);
    console.log("Text Highlighted in useEditor:", text);
    // Potentially, this could also trigger other actions, 
    // like passing the text to a chat context or an analysis service.
  }, []);

  const clearHighlightedText = useCallback(() => {
    setHighlightedText(null);
  }, []);

  return {
    editorContent,
    setEditorContent,
    highlightedText,
    handleTextHighlighted,
    clearHighlightedText,
  };
}; 