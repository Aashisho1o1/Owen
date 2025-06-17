/**
 * ChatPane Component - Enhanced Conversational Q&A Setup
 * 
 * Main chat interface with improved highlighted text integration,
 * contextual conversation starters, and better visual presentation.
 * Now includes Cursor-style controls for Author, Focus, and Model selection.
 */

import React, { useState, useRef, useEffect, useCallback } from 'react';
import { useAppContext } from '../contexts/AppContext';
import { ChatMessage } from './chat/ChatMessage';
import { ChatInput } from './chat/ChatInput';
import { ThinkingTrail } from './chat/ThinkingTrail';

const ChatPane: React.FC = () => {
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
    checkApiConnection
  } = useAppContext();

  const [showThinkingTrail, setShowThinkingTrail] = useState(false);
  const [suggestedQuestions, setSuggestedQuestions] = useState<string[]>([]);
  const [contextualPrompts, setContextualPrompts] = useState<string[]>([]);
  const [activeDropdown, setActiveDropdown] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Control options
  const authorPersonas = [
    'Ernest Hemingway',
    'Virginia Woolf', 
    'Maya Angelou',
    'George Orwell',
    'Toni Morrison',
    'J.K. Rowling',
    'Haruki Murakami',
    'Margaret Atwood'
  ];

  const helpFocuses = [
    'Dialogue Writing',
    'Scene Description', 
    'Plot Development',
    'Character Introduction',
    'Overall Tone'
  ];

  const llmOptions = [
    'OpenAI GPT',
    'Google Gemini',
    'Anthropic Claude'
  ];

  // Generate suggested questions based on help focus and author persona
  const generateSuggestedQuestions = useCallback((focus: string) => {
    const questions: {[key: string]: string[]} = {
      "Dialogue Writing": [
        `How would ${authorPersona} improve this dialogue?`,
        `What makes dialogue sound authentic and natural?`,
        `How can I develop distinct character voices?`,
        `What dialogue techniques does ${authorPersona} use?`
      ],
      "Scene Description": [
        `How would ${authorPersona} enhance this scene?`,
        `What sensory details would strengthen this setting?`,
        `How can I create more vivid imagery?`,
        `What's ${authorPersona}'s approach to setting description?`
      ],
      "Plot Development": [
        `How would ${authorPersona} develop this plot point?`,
        `What narrative techniques would strengthen this section?`,
        `How can I build more tension here?`,
        `What's missing from this story development?`
      ],
      "Character Introduction": [
        `How would ${authorPersona} introduce this character?`,
        `What character details would make this more compelling?`,
        `How can I establish this character's voice more distinctly?`,
        `What character development techniques should I use?`
      ],
      "Overall Tone": [
        `How would ${authorPersona} adjust the tone here?`,
        `What stylistic changes would improve consistency?`,
        `How can I modify the mood of this section?`,
        `What tone should I aim for in this piece?`
      ]
    };

    setSuggestedQuestions(questions[focus] || questions["Overall Tone"]);
  }, [authorPersona]);

  // Generate contextual prompts when text is highlighted
  const generateContextualPrompts = useCallback((text: string, focus: string) => {
    if (!text) {
      setContextualPrompts([]);
      return;
    }

    const prompts = [
      `Analyze this text in the style of ${authorPersona}`,
      `How would ${authorPersona} rewrite this passage?`,
      `What specific improvements would you make to this text?`,
      `Critique this writing focusing on ${focus.toLowerCase()}`,
      `What writing techniques are used here and how can they be improved?`
    ];

    setContextualPrompts(prompts);
  }, [authorPersona]);

  // Auto-scroll to bottom when messages change
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, streamText]);

  // Generate suggestions when focus changes
  useEffect(() => {
    generateSuggestedQuestions(helpFocus);
  }, [helpFocus, generateSuggestedQuestions]);

  // Generate contextual prompts when text is highlighted
  useEffect(() => {
    if (highlightedText) {
      generateContextualPrompts(highlightedText, helpFocus);
    } else {
      setContextualPrompts([]);
    }
  }, [highlightedText, helpFocus, generateContextualPrompts]);

  const handleSendMessageWrapper = (message: string) => {
    let finalMessage = message;

    // If there's highlighted text and it's not already in the message, include it for context
    if (highlightedText && !message.includes(highlightedText)) {
      finalMessage = `${message}\n\nSelected text: "${highlightedText}"`;
    }

    console.log("Sending message:", finalMessage);
    handleSendMessage(finalMessage);
  };

  // Handle automatic message sending from highlighted text
  useEffect(() => {
    const handleSendChatMessage = (event: CustomEvent) => {
      const { message, highlightedText: eventHighlightedText, highlightId } = event.detail;
      
      // Send the message automatically
      handleSendMessageWrapper(message);
    };

    window.addEventListener('sendChatMessage', handleSendChatMessage as EventListener);

    return () => {
      window.removeEventListener('sendChatMessage', handleSendChatMessage as EventListener);
    };
  }, [handleSendMessageWrapper]);

  const handleQuickQuestion = (questionTemplate: string) => {
    let finalMessage = questionTemplate;
    
    // If there's highlighted text, include it in the context
    if (highlightedText) {
      finalMessage = `${questionTemplate}\n\nSelected text: "${highlightedText}"`;
    }
    
    handleSendMessageWrapper(finalMessage);
  };

  const toggleThinkingTrail = () => {
    setShowThinkingTrail(!showThinkingTrail);
  };

  const toggleDropdown = (dropdown: string) => {
    setActiveDropdown(activeDropdown === dropdown ? null : dropdown);
  };

  const handleSelection = (type: string, value: string) => {
    switch (type) {
      case 'persona':
        setAuthorPersona(value);
        break;
      case 'focus':
        setHelpFocus(value);
        break;
      case 'model':
        setSelectedLLM(value);
        break;
    }
    setActiveDropdown(null);
  };

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = () => {
      setActiveDropdown(null);
    };

    if (activeDropdown) {
      document.addEventListener('mousedown', handleClickOutside);
      return () => {
        document.removeEventListener('mousedown', handleClickOutside);
      };
    }
  }, [activeDropdown]);



  return (
    <div className="chat-container">
      {/* Chat Header with Cursor-style Controls */}
      <div className="chat-header">
        <h2 className="chat-title">💬 AI Writing Assistant</h2>
        
        {/* Chat Controls */}
        <div className="chat-controls">
          {/* Author Persona */}
          <div className="control-icon-group">
            <button
              className={`control-icon-button ${activeDropdown === 'persona' ? 'active' : ''}`}
              onClick={() => toggleDropdown('persona')}
              title={`Author Persona: ${authorPersona}`}
              aria-expanded={activeDropdown === 'persona'}
              aria-haspopup="true"
            >
              <div className="control-button-content">
                <span className="control-icon">👤</span>
              </div>
            </button>
            {activeDropdown === 'persona' && (
              <div className="control-dropdown" role="menu">
                {authorPersonas.map((persona) => (
                  <button
                    key={persona}
                    className={`dropdown-option ${authorPersona === persona ? 'selected' : ''}`}
                    onClick={() => handleSelection('persona', persona)}
                    role="menuitem"
                  >
                    {persona}
                  </button>
                ))}
              </div>
            )}
          </div>

          {/* Help Focus */}
          <div className="control-icon-group">
            <button
              className={`control-icon-button ${activeDropdown === 'focus' ? 'active' : ''}`}
              onClick={() => toggleDropdown('focus')}
              title={`Help Focus: ${helpFocus}`}
              aria-expanded={activeDropdown === 'focus'}
              aria-haspopup="true"
            >
              <div className="control-button-content">
                <span className="control-icon">🎯</span>
              </div>
            </button>
            {activeDropdown === 'focus' && (
              <div className="control-dropdown" role="menu">
                {helpFocuses.map((focus) => (
                  <button
                    key={focus}
                    className={`dropdown-option ${helpFocus === focus ? 'selected' : ''}`}
                    onClick={() => handleSelection('focus', focus)}
                    role="menuitem"
                  >
                    {focus}
                  </button>
                ))}
              </div>
            )}
          </div>

          {/* AI Model */}
          <div className="control-icon-group">
            <button
              className={`control-icon-button ${activeDropdown === 'model' ? 'active' : ''}`}
              onClick={() => toggleDropdown('model')}
              title={`AI Model: ${selectedLLM}`}
              aria-expanded={activeDropdown === 'model'}
              aria-haspopup="true"
            >
              <div className="control-button-content">
                <span className="control-icon">🤖</span>
              </div>
            </button>
            {activeDropdown === 'model' && (
              <div className="control-dropdown" role="menu">
                {llmOptions.map((model) => (
                  <button
                    key={model}
                    className={`dropdown-option ${selectedLLM === model ? 'selected' : ''}`}
                    onClick={() => handleSelection('model', model)}
                    role="menuitem"
                  >
                    {model}
                  </button>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
      
      {/* Messages Container */}
      <div className="messages-container">
        {/* Welcome Message - Show when no messages */}
        {messages.length === 0 && (
          <div className="welcome-message">
            <div className="welcome-avatar">
              <svg xmlns="http://www.w3.org/2000/svg" width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path>
                <circle cx="12" cy="7" r="4"></circle>
              </svg>
            </div>
            <div className="welcome-content">
              <h3>Hello! I'm {authorPersona}</h3>
              <p>I'm here to help you perfect your writing, focusing on <strong>{helpFocus.toLowerCase()}</strong>. 
                 Highlight text in your document to get specific feedback, or ask me general questions about writing craft.</p>
              
              {/* Show general conversation starters when no text is highlighted */}
              {!highlightedText && (
                <div className="conversation-starters">
                  <h4>✨ Let's start the conversation:</h4>
                  <div className="starter-questions">
                    {suggestedQuestions.map((question, index) => (
                      <button
                        key={index}
                        className="starter-question-button"
                        onClick={() => handleSendMessageWrapper(question)}
                      >
                        {question}
                      </button>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        )}
        
        {/* Enhanced Highlighted Text Display with Contextual Prompts */}
        {highlightedText && (
          <div className="highlighted-text-box">
            <div className="highlighted-title">📝 Selected Text for Analysis:</div>
            <div className="highlighted-content">"{highlightedText}"</div>
            
            {/* Contextual prompts for highlighted text */}
            {contextualPrompts.length > 0 && (
              <div className="contextual-prompts">
                <div className="contextual-prompts-title">💡 Ask me about this text:</div>
                <div className="contextual-prompts-list">
                  {contextualPrompts.map((prompt, index) => (
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
        
        {/* Auto-scroll anchor */}
        <div ref={messagesEndRef} />
      </div>

      {/* Thinking Trail */}
      <ThinkingTrail 
        trail={thinkingTrail || undefined}
        isThinking={isThinking}
        isVisible={showThinkingTrail}
        onToggleVisibility={toggleThinkingTrail}
      />

      {/* Enhanced Chat Input */}
      <ChatInput 
        onSendMessage={handleSendMessageWrapper}
        isDisabled={isStreaming || isThinking}
        suggestedQuestions={highlightedText ? contextualPrompts : suggestedQuestions}
        highlightedText={highlightedText || undefined}
      />
    </div>
  );
};

export default ChatPane; 