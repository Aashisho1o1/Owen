/**
 * ChatPane Component - Optimized Chat Interface
 * 
 * Main chat interface with contextual conversation starters and clean controls.
 */

import React, { useState, useRef, useEffect, useCallback } from 'react';
import { useAppContext } from '../contexts/AppContext';
import { useAuth } from '../contexts/AuthContext';
import { ChatMessage } from './chat/ChatMessage';
import { ChatInput } from './chat/ChatInput';
import { ThinkingTrail } from './chat/ThinkingTrail';

// Constants moved outside component to prevent re-creation on each render
const AUTHOR_PERSONAS = [
  'Ernest Hemingway',
  'Virginia Woolf', 
  'Maya Angelou',
  'George Orwell',
  'Toni Morrison',
  'J.K. Rowling',
  'Haruki Murakami',
  'Margaret Atwood'
];

const HELP_FOCUSES = [
  'Dialogue Writing',
  'Scene Description', 
  'Plot Development',
  'Character Introduction',
  'Overall Tone'
];

const LLM_OPTIONS = [
  'OpenAI GPT',
  'Google Gemini',
  'Anthropic Claude'
];

// Question templates for each focus area
const QUESTION_TEMPLATES = {
  "Dialogue Writing": [
    "How would {author} improve this dialogue?",
    "What makes dialogue sound authentic and natural?",
    "How can I develop distinct character voices?",
    "What dialogue techniques does {author} use?"
  ],
  "Scene Description": [
    "How would {author} enhance this scene?",
    "What sensory details would strengthen this setting?",
    "How can I create more vivid imagery?",
    "What's {author}'s approach to setting description?"
  ],
  "Plot Development": [
    "How would {author} develop this plot point?",
    "What narrative techniques would strengthen this section?",
    "How can I build more tension here?",
    "What's missing from this story development?"
  ],
  "Character Introduction": [
    "How would {author} introduce this character?",
    "What character details would make this more compelling?",
    "How can I establish this character's voice more distinctly?",
    "What character development techniques should I use?"
  ],
  "Overall Tone": [
    "How would {author} adjust the tone here?",
    "What stylistic changes would improve consistency?",
    "How can I modify the mood of this section?",
    "What tone should I aim for in this piece?"
  ]
};

const CONTEXTUAL_PROMPTS = [
  "Analyze this text in the style of {author}",
  "How would {author} rewrite this passage?",
  "What specific improvements would you make to this text?",
  "Critique this writing focusing on {focus}",
  "What writing techniques are used here and how can they be improved?"
];

// Check if user is authenticated by looking for tokens
const isUserAuthenticated = () => {
  try {
    const accessToken = localStorage.getItem('owen_access_token');
    return !!accessToken;
  } catch {
    return false;
  }
};

const ChatPane: React.FC = () => {
  // Check authentication status
  const isAuthenticated = () => {
    try {
      const accessToken = localStorage.getItem('owen_access_token');
      return !!accessToken;
    } catch {
      return false;
    }
  };

  const [userAuthenticated, setUserAuthenticated] = useState(isAuthenticated());

  // Check auth status on mount and when localStorage changes
  useEffect(() => {
    const checkAuth = () => {
      setUserAuthenticated(isAuthenticated());
    };

    checkAuth();
    
    // Listen for storage changes (when user logs in/out)
    window.addEventListener('storage', checkAuth);
    
    // Also check periodically in case tokens are updated programmatically
    const interval = setInterval(checkAuth, 1000);

    return () => {
      window.removeEventListener('storage', checkAuth);
      clearInterval(interval);
    };
  }, []);

  const { 
    messages, 
    handleSendMessage, 
    thinkingTrail,
    highlightedText,
    helpFocus,
    setHelpFocus,
    authorPersona,
    setAuthorPersona,
    selectedLLM,
    setSelectedLLM,
    isStreaming,
    streamText,
    isThinking,
    chatApiError,
    apiGlobalError,
    checkApiConnection,
    showAuthModal,
    setShowAuthModal,
    setAuthMode
  } = useAppContext();

  const [showThinkingTrail, setShowThinkingTrail] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Memoized suggested questions to prevent unnecessary recalculations
  const suggestedQuestions = useCallback(() => {
    const templates = QUESTION_TEMPLATES[helpFocus as keyof typeof QUESTION_TEMPLATES] || QUESTION_TEMPLATES["Overall Tone"];
    return templates.map(template => template.replace('{author}', authorPersona));
  }, [helpFocus, authorPersona]);

  // Memoized contextual prompts for highlighted text
  const contextualPrompts = useCallback(() => {
    if (!highlightedText) return [];
    return CONTEXTUAL_PROMPTS.map(template => 
      template.replace('{author}', authorPersona).replace('{focus}', helpFocus.toLowerCase())
    );
  }, [highlightedText, authorPersona, helpFocus]);

  // Auto-scroll to bottom when messages change
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, streamText]);

  const handleSendMessageWrapper = useCallback((message: string) => {
    let finalMessage = message;
    
    // Include highlighted text context if available and not already included
    if (highlightedText && !message.includes(highlightedText)) {
      finalMessage = `${message}\n\nSelected text: "${highlightedText}"`;
    }
    
    handleSendMessage(finalMessage);
  }, [highlightedText, handleSendMessage]);

  const handleQuickQuestion = useCallback((questionTemplate: string) => {
    let finalMessage = questionTemplate;
    
    // Include highlighted text context if available
    if (highlightedText) {
      finalMessage = `${questionTemplate}\n\nSelected text: "${highlightedText}"`;
    }
    
    handleSendMessageWrapper(finalMessage);
  }, [highlightedText, handleSendMessageWrapper]);

  const toggleThinkingTrail = useCallback(() => {
    setShowThinkingTrail(prev => !prev);
  }, []);

  // Handle automatic message sending from highlighted text
  useEffect(() => {
    const handleSendChatMessage = (event: CustomEvent) => {
      const { message } = event.detail;
      handleSendMessageWrapper(message);
    };

    window.addEventListener('sendChatMessage', handleSendChatMessage as EventListener);
    return () => window.removeEventListener('sendChatMessage', handleSendChatMessage as EventListener);
  }, [handleSendMessageWrapper]);

  return (
    <div className="chat-container">
      {/* Chat Header with Controls */}
      <div className="chat-header">
        <div className="chat-title">
          <span className="title-icon">💬</span>
          AI Writing Assistant
        </div>
        
        <div className="chat-controls-simple">
          <div className="control-select-group">
            <label>👤</label>
            <select 
              value={authorPersona} 
              onChange={(e) => setAuthorPersona(e.target.value)}
              className="control-select"
              aria-label="Select author persona"
            >
              {AUTHOR_PERSONAS.map((persona) => (
                <option key={persona} value={persona}>
                  {persona}
                </option>
              ))}
            </select>
          </div>
          
          <div className="control-select-group">
            <label>🎯</label>
            <select 
              value={helpFocus} 
              onChange={(e) => setHelpFocus(e.target.value)}
              className="control-select"
              aria-label="Select writing focus"
            >
              {HELP_FOCUSES.map((focus) => (
                <option key={focus} value={focus}>
                  {focus}
                </option>
              ))}
            </select>
          </div>
          
          <div className="control-select-group">
            <label>🤖</label>
            <select 
              value={selectedLLM} 
              onChange={(e) => setSelectedLLM(e.target.value)}
              className="control-select"
              aria-label="Select AI model"
            >
              {LLM_OPTIONS.map((model) => (
                <option key={model} value={model}>
                  {model}
                </option>
              ))}
            </select>
          </div>
        </div>
      </div>
      
      {/* Messages Container */}
      <div className="messages-container">
        {/* Enhanced Highlighted Text Display */}
        {highlightedText && (
          <div className="highlighted-text-box">
            <div className="highlighted-title">📝 Selected Text for Analysis:</div>
            <div className="highlighted-content">"{highlightedText}"</div>
            
            {contextualPrompts().length > 0 && (
              <div className="contextual-prompts">
                <div className="contextual-prompts-title">💡 Ask me about this text:</div>
                <div className="contextual-prompts-list">
                  {contextualPrompts().map((prompt, index) => (
                    <button
                      key={index}
                      className="contextual-prompt-button"
                      onClick={() => handleQuickQuestion(prompt)}
                    >
                      {prompt}
                    </button>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}
        
        {/* API Error Display */}
        {(chatApiError || apiGlobalError) && (
          <div className="chat-error-box">
            <div className="error-icon">⚠️</div>
            <div className="error-content">
              <div className="error-title">Connection Issue</div>
              <div className="error-message">
                {chatApiError || apiGlobalError}
              </div>
              <button 
                className="test-connection-button"
                onClick={async () => {
                  try {
                    await checkApiConnection();
                    handleSendMessageWrapper("Test connection - please respond with a simple greeting.");
                  } catch (error) {
                    console.error('Connection test failed:', error);
                  }
                }}
              >
                🔄 Test Connection
              </button>
            </div>
          </div>
        )}
        
        {/* Chat Messages */}
        {messages.map((msg, index) => (
          <ChatMessage 
            key={index} 
            message={msg}
          />
        ))}
        
        {/* Streaming Message */}
        {isStreaming && streamText && (
          <div className="message ai-message streaming">
            <div className="message-avatar">
              <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <rect x="3" y="4" width="18" height="18" rx="2" ry="2"></rect>
                <line x1="16" y1="2" x2="16" y2="6"></line>
                <line x1="8" y1="2" x2="8" y2="6"></line>
                <line x1="3" y1="10" x2="21" y2="10"></line>
              </svg>
            </div>
            <div className="message-content">
              {streamText}
              <span className="typing-cursor">|</span>
            </div>
          </div>
        )}
        
        <div ref={messagesEndRef} />
      </div>

      {/* Thinking Trail */}
      <ThinkingTrail 
        trail={thinkingTrail || undefined}
        isThinking={isThinking}
        isVisible={showThinkingTrail}
        onToggleVisibility={toggleThinkingTrail}
      />

      {/* Chat Input */}
      <ChatInput 
        onSendMessage={handleSendMessageWrapper}
        isDisabled={isStreaming || isThinking}
        suggestedQuestions={highlightedText ? contextualPrompts() : suggestedQuestions()}
        highlightedText={highlightedText || undefined}
      />
    </div>
  );
};

export default ChatPane; 