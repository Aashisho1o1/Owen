import { useState, useEffect } from 'react';
import Editor from './components/Editor';
import ChatPane from './components/ChatPane';
import Controls from './components/Controls';
import api, { ChatMessage } from './services/api';
import './App.css';

// Type for API errors
interface ApiError {
  response?: {
    status: number;
    statusText: string;
    data: unknown;
  };
  request?: unknown;
  message: string;
}

function App() {
  const [editorContent, setEditorContent] = useState('');
  const [authorPersona, setAuthorPersona] = useState('Ernest Hemingway');
  const [helpFocus, setHelpFocus] = useState('Dialogue Writing');
  const [messages, setMessages] = useState<ChatMessage[]>([
    { 
      role: 'assistant', 
      content: `Hello, I'm your ${authorPersona} AI writing assistant. I'll help you with your ${helpFocus.toLowerCase()}. What would you like to ask?` 
    }
  ]);
  const [fillInTheBlanks, setFillInTheBlanks] = useState<string | null>(null);
  const [reasoning, setReasoning] = useState<string | null>(null);
  const [apiError, setApiError] = useState<string | null>(null);
  const [highlightedText, setHighlightedText] = useState<string | null>(null);
  const [isStreaming, setIsStreaming] = useState(false);
  const [streamText, setStreamText] = useState('');
  const [streamIndex, setStreamIndex] = useState(0);
  const [fullResponse, setFullResponse] = useState('');
  const [isThinking, setIsThinking] = useState(false);

  // Check API connection on startup
  useEffect(() => {
    const checkApiConnection = async () => {
      try {
        await api.healthCheck();
        setApiError(null);
      } catch (error) {
        console.error('API health check failed:', error);
        setApiError('Could not connect to the backend API. Please make sure the server is running.');
      }
    };

    checkApiConnection();
  }, []);

  // Initialize assistant message when author or focus changes
  useEffect(() => {
    setMessages([
      { 
        role: 'assistant', 
        content: `Hello, I'm your ${authorPersona} AI writing assistant. I'll help you with your ${helpFocus.toLowerCase()}. What would you like to ask?` 
      }
    ]);
    setFillInTheBlanks(null);
    setReasoning(null);
  }, [authorPersona, helpFocus]);

  const handleSendMessage = async (message: string) => {
    // Add user message to chat
    const updatedMessages = [
      ...messages,
      { role: 'user' as const, content: message }
    ];
    
    setMessages(updatedMessages);
    setApiError(null);
    setIsStreaming(false);
    setStreamText('');
    setStreamIndex(0);
    setIsThinking(true);
    
    try {
      // Send request to API
      console.log('Sending request to API:', {
        message,
        editor_text: editorContent,
        author_persona: authorPersona,
        help_focus: helpFocus,
        chat_history: updatedMessages
      });
      
      const response = await api.chat({
        message,
        editor_text: editorContent,
        author_persona: authorPersona,
        help_focus: helpFocus,
        chat_history: updatedMessages
      });
      
      console.log('API response:', response);
      
      // Start streaming response
      setIsThinking(false);
      setIsStreaming(true);
      setFullResponse(response.dialogue_response);
      
      // Set fill-in-the-blanks suggestion and reasoning
      setFillInTheBlanks(response.fill_in_the_blanks_suggestion);
      setReasoning(response.reasoning);
      
      // Clear the highlighted text after getting a response
      setHighlightedText(null);
    } catch (error: unknown) {
      console.error('Error sending message:', error);
      // Add error message to chat
      setMessages([
        ...updatedMessages,
        { role: 'assistant' as const, content: 'Sorry, I encountered an error processing your request. Please try again.' }
      ]);
      
      const apiError = error as ApiError;
      if (apiError.response) {
        console.error('Error response:', apiError.response.data);
        setApiError(`API error: ${apiError.response.status} ${apiError.response.statusText} - ${JSON.stringify(apiError.response.data)}`);
      } else if (apiError.request) {
        setApiError('No response received from the server. Please check if the backend is running.');
      } else {
        setApiError(`Error: ${apiError.message}`);
      }
      setIsThinking(false);
      setIsStreaming(false);
    }
  };

  // Character-by-character streaming effect
  useEffect(() => {
    if (!isStreaming || streamIndex >= fullResponse.length) {
      if (isStreaming && streamIndex >= fullResponse.length) {
        // Streaming complete, add message to chat
        setMessages(prev => [
          ...prev,
          { role: 'assistant' as const, content: fullResponse }
        ]);
        setIsStreaming(false);
      }
      return;
    }
    
    const typingSpeed = Math.random() * 30 + 20; // Random speed between 20-50ms for natural effect
    const timer = setTimeout(() => {
      setStreamText(fullResponse.substring(0, streamIndex + 1));
      setStreamIndex(prevIndex => prevIndex + 1);
    }, typingSpeed);
    
    return () => clearTimeout(timer);
  }, [isStreaming, streamIndex, fullResponse]);

  const handleSaveCheckpoint = async () => {
    try {
      await api.createCheckpoint({
        editor_text: editorContent,
        chat_history: messages
      });
      
      alert('Checkpoint saved successfully!');
    } catch (error) {
      console.error('Error saving checkpoint:', error);
      alert('Failed to save checkpoint. Please try again.');
    }
  };
  
  const handleTextHighlighted = (text: string) => {
    setHighlightedText(text);
  };

  return (
    <div className="app">
      <header className="app-header">
        <h1>Owen</h1>
      </header>
      
      <Controls
        authorPersona={authorPersona}
        helpFocus={helpFocus}
        onAuthorChange={setAuthorPersona}
        onHelpFocusChange={setHelpFocus}
        onSaveCheckpoint={handleSaveCheckpoint}
      />
      
      {apiError && (
        <div className="api-error-banner">
          <p>{apiError}</p>
        </div>
      )}
      
      <main className="app-content">
        <div className="editor-pane">
          <Editor 
            content={editorContent} 
            onChange={setEditorContent}
            onTextHighlighted={handleTextHighlighted}
          />
        </div>
        
        <div className="chat-pane">
          <ChatPane 
            messages={messages} 
            onSendMessage={handleSendMessage}
            fillInTheBlanks={fillInTheBlanks}
            reasoning={reasoning}
            highlightedText={highlightedText}
            helpFocus={helpFocus}
            authorPersona={authorPersona}
            isStreaming={isStreaming}
            streamingText={streamText}
            isThinking={isThinking}
          />
        </div>
      </main>
      
      <style>{`
        .api-error-banner {
          background-color: #fee2e2;
          color: #b91c1c;
          padding: 10px;
          margin: 0;
          text-align: center;
          border: 1px solid #fecaca;
        }
        
        /* Add these styles to fix the layout and background issues */
        .app {
          display: flex;
          flex-direction: column;
          height: 100vh;
          overflow: hidden;
        }
        
        .app-content {
          flex: 1;
          overflow: hidden;
          padding: 1.5rem;
          gap: 1.5rem;
          display: flex;
          max-height: none !important;
        }
        
        .editor-pane, .chat-pane {
          flex: 1;
          min-width: 0;
          display: flex;
          flex-direction: column;
          overflow: hidden;
          background-color: white;
        }
        
        /* This will override the ChatPane component's styles */
        .chat-pane .messages-container {
          background-color: white !important;
        }
        
        .chat-pane .chat-container {
          background-color: white !important;
        }
        
        /* Fix media queries */
        @media (max-width: 768px) {
          .app-content {
            flex-direction: column;
          }
          
          .editor-pane, .chat-pane {
            height: auto;
            flex: 1;
          }
        }
      `}</style>
    </div>
  );
}

export default App;
