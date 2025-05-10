/*
# REFACTORING PLAN

This ChatPane component is extremely large (573 lines) and should be broken down into smaller, more focused components:

1. Extract sub-components to their own files:
   - `ChatMessage.tsx` - Display a single message 
   - `ChatInput.tsx` - Handle message input and submission
   - `ThinkingTrail.tsx` - Display thinking trail
   - `ChatHeader.tsx` - Chat header with persona info

2. Create utility functions for repeated logic:
   - `utils/messageFormatting.ts` - Handle message formatting/parsing
   - `utils/streamingText.ts` - Text streaming animation logic

3. Extract styles to separate CSS files:
   - `styles/ChatPane.css`
   - `styles/ChatMessage.css`
   - etc.

Example implementation structure:

```tsx
// components/chat/ChatMessage.tsx
export const ChatMessage = ({ message, highlightedText }) => {
  return (
    <div className={`chat-message ${message.role}`}>
      <div className="message-content">{renderMessageContent(message, highlightedText)}</div>
    </div>
  );
};

// components/chat/ChatInput.tsx
export const ChatInput = ({ onSendMessage, isDisabled }) => {
  const [inputValue, setInputValue] = useState("");
  // Input handling logic...
  return (
    <div className="chat-input-container">
      <textarea value={inputValue} onChange={...} />
      <button onClick={handleSend} disabled={isDisabled}>Send</button>
    </div>
  );
};

// ChatPane.tsx (much smaller)
import { ChatMessage } from './chat/ChatMessage';
import { ChatInput } from './chat/ChatInput';
import { ThinkingTrail } from './chat/ThinkingTrail';
import { ChatHeader } from './chat/ChatHeader';
import './styles/ChatPane.css';

const ChatPane = ({ messages, onSendMessage, ...otherProps }) => {
  return (
    <div className="chat-pane">
      <ChatHeader authorPersona={otherProps.authorPersona} helpFocus={otherProps.helpFocus} />
      <div className="messages-container">
        {messages.map(message => <ChatMessage key={...} message={message} />)}
        {otherProps.isStreaming && <StreamingMessage text={otherProps.streamingText} />}
      </div>
      <ThinkingTrail trail={otherProps.thinkingTrail} isThinking={otherProps.isThinking} />
      <ChatInput onSendMessage={onSendMessage} isDisabled={otherProps.isStreaming || otherProps.isThinking} />
    </div>
  );
};
```

Benefits:
- Improved readability with smaller, focused components
- Better testability
- Easier maintenance
- Potential for better performance through more targeted re-renders
- Better code organization
*/

import React, { useState, useRef, useEffect, useCallback } from 'react';
import { useAppContext } from '../contexts/AppContext';

const ChatPane: React.FC = () => {
  const { 
    messages, 
    handleSendMessage, 
    thinkingTrail,
    highlightedText,
    helpFocus,
    authorPersona,
    isStreaming,
    streamText,
    isThinking
  } = useAppContext();

  const [newMessage, setNewMessage] = useState('');
  const [showThinkingTrail, setShowThinkingTrail] = useState(false);
  const [suggestedQuestions, setSuggestedQuestions] = useState<string[]>([]);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Define the generateSuggestedQuestions function with useCallback
  const generateSuggestedQuestions = useCallback((focus: string) => {
    const questions: {[key: string]: string[]} = {
      "Dialogue Writing": [
        `How would ${authorPersona} improve this dialogue?`,
        `How can I make this conversation more authentic?`,
        `What dialogue techniques would strengthen this exchange?`
      ],
      "Scene Description": [
        `How would ${authorPersona} enhance this scene description?`,
        `What sensory details could improve this setting?`,
        `How can I make this scene more vivid?`
      ],
      "Plot Development": [
        `How would ${authorPersona} develop this plot point?`,
        `What narrative techniques would strengthen this section?`,
        `How can I build more tension in this passage?`
      ],
      "Character Introduction": [
        `How would ${authorPersona} introduce this character better?`,
        `What character details would make this more compelling?`,
        `How can I establish this character's voice more distinctly?`
      ],
      "Overall Tone": [
        `How would ${authorPersona} adjust the tone of this passage?`,
        `What stylistic changes would make this more consistent with ${authorPersona}'s voice?`,
        `How can I modify the mood of this section?`
      ]
    };

    setSuggestedQuestions(questions[focus] || questions["Overall Tone"]);
  }, [authorPersona]);

  // Auto-scroll to bottom when messages change
  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Generate suggested questions when text is highlighted or focus changes
  useEffect(() => {
    if (highlightedText) {
      generateSuggestedQuestions(helpFocus);
    }
  }, [highlightedText, helpFocus, generateSuggestedQuestions]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const onSendMessageHandle = (e: React.FormEvent) => {
    e.preventDefault();
    if (newMessage.trim()) {
      console.log("Sending message:", newMessage);
      handleSendMessage(newMessage.trim());
      setNewMessage('');
    }
  };

  const handleSelectQuestion = (question: string) => {
    setNewMessage(question);
  };

  return (
    <div className="chat-container">
      <div className="chat-header">
        <h2>AI Author Chat</h2>
        <div className="header-buttons">
          {thinkingTrail && (
            <button 
              className="toggle-thinking-button"
              onClick={() => setShowThinkingTrail(!showThinkingTrail)}
            >
              {showThinkingTrail ? 'Hide' : 'Show'} AI Thinking Trail
            </button>
          )}
        </div>
      </div>
      
      <div className="messages-container">
        {highlightedText && (
          <div className="highlighted-text-box">
            <div className="highlighted-title">Selected Text:</div>
            <div className="highlighted-content">{highlightedText}</div>
          </div>
        )}
        
        {messages.map((msg, index) => (
          <div 
            key={index} 
            className={`message ${msg.role === 'user' ? 'user-message' : 'ai-message'}`}
          >
            {msg.role === 'assistant' && (
              <div className="message-avatar">
                <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <rect x="3" y="4" width="18" height="18" rx="2" ry="2"></rect>
                  <line x1="16" y1="2" x2="16" y2="6"></line>
                  <line x1="8" y1="2" x2="8" y2="6"></line>
                  <line x1="3" y1="10" x2="21" y2="10"></line>
                </svg>
              </div>
            )}
            <div className="message-content">
              {renderMessage(msg)}
            </div>
          </div>
        ))}

        {isStreaming && (
          <div className="message ai-message streaming-message">
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
              <span className="typing-cursor"></span>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {showThinkingTrail && thinkingTrail && (
        <div className="thinking-trail">
          <div className="thinking-trail-header">AI Thinking Process:</div>
          <div className="thinking-trail-content">{thinkingTrail}</div>
        </div>
      )}

      {isThinking && (
        <div className="thinking-indicator">
          <div className="thinking-text">
            <span>Owen is thinking</span>
            <span className="thinking-dots">
              <span className="dot">.</span>
              <span className="dot">.</span>
              <span className="dot">.</span>
            </span>
          </div>
        </div>
      )}
      
      {highlightedText && suggestedQuestions.length > 0 && (
        <div className="suggested-questions">
          <div className="suggested-title">Suggested questions:</div>
          <div className="questions-list">
            {suggestedQuestions.map((question, index) => (
              <button 
                key={index}
                className="question-item"
                onClick={() => handleSelectQuestion(question)}
              >
                {question}
              </button>
            ))}
          </div>
        </div>
      )}

      <div className="chat-input">
        <form onSubmit={onSendMessageHandle}>
          <textarea
            value={newMessage}
            onChange={(e) => setNewMessage(e.target.value)}
            placeholder="Ask Owen for writing help..."
            className="chat-textarea"
            disabled={isStreaming || isThinking}
          />
          <button 
            type="submit" 
            className="send-button"
            disabled={!newMessage.trim() || isStreaming || isThinking}
          >
            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <line x1="22" y1="2" x2="11" y2="13"></line>
              <polygon points="22 2 15 22 11 13 2 9 22 2"></polygon>
            </svg>
          </button>
        </form>
      </div>

      <style>{`
        .chat-container {
          display: flex;
          flex-direction: column;
          height: 100%;
          border-radius: var(--rounded-xl);
          overflow: hidden;
          background-color: white;
        }
        
        .chat-header {
          padding: 12px 16px;
          border-bottom: 1px solid #e2e8f0;
          background-color: white;
          display: flex;
          justify-content: space-between;
          align-items: center;
        }
        
        .chat-header h2 {
          margin: 0;
          font-size: 1.125rem;
          font-weight: 600;
          color: var(--text-primary);
        }
        
        .toggle-reasoning-button {
          background-color: var(--bg-secondary);
          border: 1px solid #e2e8f0;
          border-radius: var(--rounded-md);
          padding: 4px 8px;
          font-size: 0.75rem;
          cursor: pointer;
          color: var(--text-secondary);
          transition: all 0.2s;
        }
        
        .toggle-reasoning-button:hover {
          background-color: var(--bg-primary);
          color: var(--text-primary);
        }
        
        .messages-container {
          flex: 1;
          overflow-y: auto;
          padding: 20px;
          display: flex;
          flex-direction: column;
          gap: 16px;
          background-color: white;
        }
        
        .highlighted-text-box {
          border: 2px dashed var(--primary-light);
          border-radius: var(--rounded-lg);
          padding: 16px;
          background-color: rgba(99, 102, 241, 0.05);
          width: 100%;
        }
        
        .highlighted-title {
          font-weight: 600;
          margin-bottom: 8px;
          color: var(--primary-dark);
          font-size: 0.875rem;
        }
        
        .highlighted-content {
          white-space: pre-wrap;
          color: var(--text-primary);
          font-family: var(--font-sans);
          line-height: 1.5;
        }
        
        .suggested-questions {
          border: 1px solid #e2e8f0;
          border-radius: var(--rounded-lg);
          padding: 16px;
          background-color: white;
          width: 100%;
          box-shadow: var(--shadow-sm);
        }
        
        .suggested-questions-title {
          font-weight: 600;
          margin-bottom: 12px;
          color: var(--text-primary);
          font-size: 0.875rem;
        }
        
        .question-buttons {
          display: flex;
          flex-direction: column;
          gap: 8px;
        }
        
        .question-button {
          text-align: left;
          padding: 8px 12px;
          background-color: var(--bg-secondary);
          border: 1px solid #e2e8f0;
          border-radius: var(--rounded-md);
          cursor: pointer;
          font-size: 0.875rem;
          color: var(--text-primary);
          transition: all 0.2s;
        }
        
        .question-button:hover {
          background-color: var(--primary-light);
          color: white;
          border-color: var(--primary-light);
        }
        
        .message {
          display: flex;
          align-items: flex-start;
          gap: 10px;
          max-width: 90%;
        }
        
        .message-avatar {
          width: 32px;
          height: 32px;
          border-radius: var(--rounded-md);
          background-color: var(--primary-light);
          color: white;
          display: flex;
          align-items: center;
          justify-content: center;
          flex-shrink: 0;
        }
        
        .message-bubble {
          padding: 12px 16px;
          border-radius: 18px;
          word-wrap: break-word;
          position: relative;
          box-shadow: var(--shadow-sm);
        }
        
        .user-message {
          margin-left: auto;
          flex-direction: row-reverse;
        }
        
        .user-message .message-bubble {
          background-color: var(--primary-color);
          color: white;
          border-bottom-right-radius: 4px;
        }
        
        .ai-message .message-bubble {
          background-color: white;
          color: var(--text-primary);
          border-bottom-left-radius: 4px;
        }
        
        .cursor-blink {
          display: inline-block;
          animation: blink 1s step-end infinite;
          color: var(--primary-color);
          font-weight: bold;
        }
        
        @keyframes blink {
          from, to { opacity: 1; }
          50% { opacity: 0; }
        }
        
        .reasoning-box {
          border: 1px solid #e2e8f0;
          border-radius: var(--rounded-lg);
          padding: 16px;
          margin: 8px 0;
          background-color: white;
          width: 90%;
          box-shadow: var(--shadow-sm);
          border-left: 3px solid var(--secondary-color);
        }
        
        .reasoning-title {
          font-weight: 600;
          margin-bottom: 8px;
          color: var(--text-primary);
          display: flex;
          align-items: center;
          gap: 6px;
        }
        
        .input-container {
          display: flex;
          padding: 16px;
          border-top: 1px solid #e2e8f0;
          background-color: white;
          position: relative;
          z-index: 10;
        }
        
        .message-input {
          flex: 1;
          padding: 12px 16px;
          border: 1px solid #e2e8f0;
          border-radius: 24px;
          font-size: 0.9375rem;
          outline: none;
          background-color: #f8fafc;
          transition: all 0.2s;
          position: relative;
          z-index: 11;
          color: var(--text-primary);
        }
        
        .message-input::placeholder {
          color: var(--text-secondary);
          opacity: 0.8;
        }
        
        .message-input.has-text {
          background-color: white;
          border-color: var(--primary-light);
          box-shadow: 0 0 0 2px rgba(99, 102, 241, 0.1);
        }
        
        .message-input:focus {
          border-color: var(--primary-light);
          box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.15);
        }
        
        .message-input:disabled {
          opacity: 0.7;
          cursor: not-allowed;
        }
        
        .send-button {
          margin-left: 8px;
          width: 44px;
          height: 44px;
          background-color: var(--primary-color);
          color: white;
          border: none;
          border-radius: 50%;
          cursor: pointer;
          font-weight: bold;
          display: flex;
          align-items: center;
          justify-content: center;
          transition: all 0.2s;
          box-shadow: var(--shadow-sm);
        }
        
        .send-button:hover {
          background-color: var(--primary-dark);
          transform: translateY(-1px);
          box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
        }
        
        .send-button:active {
          transform: translateY(0);
        }
        
        .send-button:disabled {
          background-color: #cbd5e1;
          cursor: not-allowed;
          transform: none;
          box-shadow: none;
        }
        
        .streaming-message {
          opacity: 0.95;
        }

        .thinking-message {
          opacity: 0.7;
        }
        
        .thinking-content {
          display: flex;
          align-items: center;
          justify-content: center;
          min-height: 24px;
        }
        
        .thinking-dots {
          display: flex;
        }
        
        .thinking-dots span {
          font-size: 24px;
          line-height: 1;
          margin: 0 2px;
          animation: pulse 1.4s infinite;
          animation-fill-mode: both;
        }
        
        .thinking-dots span:nth-child(2) {
          animation-delay: 0.2s;
        }
        
        .thinking-dots span:nth-child(3) {
          animation-delay: 0.4s;
        }
        
        @keyframes pulse {
          0%, 100% {
            transform: scale(0.7);
            opacity: 0.5;
          }
          50% {
            transform: scale(1);
            opacity: 1;
          }
        }
        
        @media (max-width: 768px) {
          .messages-container {
            padding: 16px;
          }
          
          .message {
            max-width: 95%;
          }
        }
      `}</style>
    </div>
  );
};

// Helper function to render message content with proper formatting
const renderMessage = (message: { role: string; content: string }) => {
  // Split by code blocks (if any)
  const parts = message.content.split(/```(?:([a-zA-Z0-9]+)\n)?([\s\S]*?)```/g);
  
  // If no code blocks, return the content directly
  if (parts.length === 1) {
    return <p>{renderTextWithLineBreaks(message.content)}</p>;
  }
  
  // Render the message with code blocks
  return (
    <div>
      {parts.map((part, idx) => {
        // Regular text part
        if (idx % 3 === 0) {
          return part ? <p key={idx}>{renderTextWithLineBreaks(part)}</p> : null;
        }
        // Language specification (parts[1], parts[4], etc.)
        else if (idx % 3 === 1) {
          return null; // We use this in the next part
        }
        // Code block content (parts[2], parts[5], etc.)
        else {
          const language = parts[idx - 1] || '';
          return (
            <pre key={idx} className={`code-block${language ? ` language-${language}` : ''}`}>
              <code>{part}</code>
            </pre>
          );
        }
      })}
    </div>
  );
};

// Helper function to render text with line breaks
const renderTextWithLineBreaks = (text: string) => {
  return text.split('\n').map((line, i) => (
    <React.Fragment key={i}>
      {line}
      {i < text.split('\n').length - 1 && <br />}
    </React.Fragment>
  ));
};

export default ChatPane; 