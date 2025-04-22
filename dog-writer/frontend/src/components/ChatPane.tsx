import React, { useState, useRef, useEffect } from 'react';
import { ChatMessage } from '../services/api';

interface ChatPaneProps {
  messages: ChatMessage[];
  onSendMessage: (message: string) => void;
  fillInTheBlanks?: string | null;
  reasoning?: string | null;
  highlightedText?: string | null;
  helpFocus?: string;
  authorPersona?: string;
  isStreaming?: boolean;
  streamingText?: string;
  isThinking?: boolean;
}

const ChatPane: React.FC<ChatPaneProps> = ({ 
  messages, 
  onSendMessage, 
  fillInTheBlanks,
  reasoning,
  highlightedText,
  helpFocus = "Dialogue Writing",
  authorPersona = "Ernest Hemingway",
  isStreaming = false,
  streamingText = '',
  isThinking = false
}) => {
  const [newMessage, setNewMessage] = useState('');
  const [showReasoning, setShowReasoning] = useState(false);
  const [suggestedQuestions, setSuggestedQuestions] = useState<string[]>([]);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom when messages change
  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Generate suggested questions when text is highlighted or focus changes
  useEffect(() => {
    if (highlightedText) {
      generateSuggestedQuestions(helpFocus);
    }
  }, [highlightedText, helpFocus, authorPersona]);

  const generateSuggestedQuestions = (focus: string) => {
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
  };

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const handleSendMessage = (e: React.FormEvent) => {
    e.preventDefault();
    if (newMessage.trim()) {
      console.log("Sending message:", newMessage);
      onSendMessage(newMessage.trim());
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
        {reasoning && (
          <button 
            className="toggle-reasoning-button"
            onClick={() => setShowReasoning(!showReasoning)}
          >
            {showReasoning ? 'Hide' : 'Show'} AI Reasoning
          </button>
        )}
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
                  <path d="M8 14h.01"></path>
                  <path d="M12 14h.01"></path>
                  <path d="M16 14h.01"></path>
                  <path d="M8 18h.01"></path>
                  <path d="M12 18h.01"></path>
                  <path d="M16 18h.01"></path>
                </svg>
              </div>
            )}
            <div className="message-bubble">
              <div className="message-content">{msg.content}</div>
            </div>
          </div>
        ))}
        
        {isThinking && (
          <div className="message ai-message thinking-message">
            <div className="message-avatar">
              <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <rect x="3" y="4" width="18" height="18" rx="2" ry="2"></rect>
                <line x1="16" y1="2" x2="16" y2="6"></line>
                <line x1="8" y1="2" x2="8" y2="6"></line>
                <line x1="3" y1="10" x2="21" y2="10"></line>
                <path d="M8 14h.01"></path>
                <path d="M12 14h.01"></path>
                <path d="M16 14h.01"></path>
                <path d="M8 18h.01"></path>
                <path d="M12 18h.01"></path>
                <path d="M16 18h.01"></path>
              </svg>
            </div>
            <div className="message-bubble">
              <div className="message-content thinking-content">
                <span className="thinking-dots">
                  <span>.</span><span>.</span><span>.</span>
                </span>
              </div>
            </div>
          </div>
        )}
        
        {isStreaming && (
          <div className="message ai-message streaming-message">
            <div className="message-avatar">
              <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <rect x="3" y="4" width="18" height="18" rx="2" ry="2"></rect>
                <line x1="16" y1="2" x2="16" y2="6"></line>
                <line x1="8" y1="2" x2="8" y2="6"></line>
                <line x1="3" y1="10" x2="21" y2="10"></line>
                <path d="M8 14h.01"></path>
                <path d="M12 14h.01"></path>
                <path d="M16 14h.01"></path>
                <path d="M8 18h.01"></path>
                <path d="M12 18h.01"></path>
                <path d="M16 18h.01"></path>
              </svg>
            </div>
            <div className="message-bubble">
              <div className="message-content">{streamingText}<span className="cursor-blink">|</span></div>
            </div>
          </div>
        )}
        
        {showReasoning && reasoning && (
          <div className="reasoning-box">
            <div className="reasoning-title">
              <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"></polygon>
              </svg>
              AI Reasoning
            </div>
            <div>{reasoning}</div>
          </div>
        )}
        
        {fillInTheBlanks && (
          <div className="suggestion-box">
            <div className="suggestion-title">
              <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path>
                <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path>
              </svg>
              Suggested Text
            </div>
            <div>{fillInTheBlanks}</div>
          </div>
        )}
        
        {highlightedText && suggestedQuestions.length > 0 && (
          <div className="suggested-questions">
            <div className="suggested-questions-title">Suggested Questions:</div>
            <div className="question-buttons">
              {suggestedQuestions.map((question, index) => (
                <button 
                  key={index} 
                  className="question-button"
                  onClick={() => handleSelectQuestion(question)}
                >
                  {question}
                </button>
              ))}
            </div>
          </div>
        )}
        
        <div ref={messagesEndRef} />
      </div>
      
      <form className="input-container" onSubmit={handleSendMessage}>
        <input
          type="text"
          value={newMessage}
          onChange={(e) => setNewMessage(e.target.value)}
          placeholder={highlightedText ? "Ask about the highlighted text..." : "Ask your AI author..."}
          className={`message-input ${newMessage ? 'has-text' : ''}`}
          disabled={isStreaming}
        />
        <button type="submit" className="send-button" disabled={!newMessage.trim() || isStreaming}>
          <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <line x1="22" y1="2" x2="11" y2="13"></line>
            <polygon points="22 2 15 22 11 13 2 9 22 2"></polygon>
          </svg>
        </button>
      </form>
      
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
        
        .reasoning-box, .suggestion-box {
          border: 1px solid #e2e8f0;
          border-radius: var(--rounded-lg);
          padding: 16px;
          margin: 8px 0;
          background-color: white;
          width: 90%;
          box-shadow: var(--shadow-sm);
        }
        
        .reasoning-title, .suggestion-title {
          font-weight: 600;
          margin-bottom: 8px;
          color: var(--text-primary);
          display: flex;
          align-items: center;
          gap: 6px;
        }
        
        .reasoning-box {
          border-left: 3px solid var(--secondary-color);
        }
        
        .suggestion-box {
          border-left: 3px solid var(--accent-color);
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

export default ChatPane; 