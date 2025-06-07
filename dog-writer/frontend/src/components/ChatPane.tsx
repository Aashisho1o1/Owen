/**
 * ChatPane Component - Refactored
 * 
 * Main chat interface that orchestrates smaller, focused components.
 * Reduced from 656 lines to ~150 lines through proper component composition.
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
    authorPersona,
    isStreaming,
    streamText,
    isThinking
  } = useAppContext();

  const [showThinkingTrail, setShowThinkingTrail] = useState(false);
  const [suggestedQuestions, setSuggestedQuestions] = useState<string[]>([]);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Generate suggested questions based on help focus and author persona
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
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, streamText]);

  // Generate suggested questions when text is highlighted
  useEffect(() => {
    if (highlightedText) {
      generateSuggestedQuestions(helpFocus);
    }
  }, [highlightedText, helpFocus, generateSuggestedQuestions]);

  const handleSendMessageWrapper = (message: string) => {
    console.log("Sending message:", message);
    handleSendMessage(message);
  };

  const toggleThinkingTrail = () => {
    setShowThinkingTrail(!showThinkingTrail);
  };

  return (
    <div className="chat-container">
      {/* Chat Header */}
      <div className="chat-header">
        <h2>AI Author Chat</h2>
        <div className="header-info">
          <span className="author-persona">with {authorPersona}</span>
          <span className="help-focus">Focus: {helpFocus}</span>
        </div>
      </div>
      
      {/* Messages Container */}
      <div className="messages-container">
        {/* Highlighted Text Display */}
        {highlightedText && (
          <div className="highlighted-text-box">
            <div className="highlighted-title">Selected Text:</div>
            <div className="highlighted-content">{highlightedText}</div>
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

      {/* Chat Input */}
      <ChatInput 
        onSendMessage={handleSendMessageWrapper}
        isDisabled={isStreaming || isThinking}
        suggestedQuestions={suggestedQuestions}
        highlightedText={highlightedText || undefined}
      />
    </div>
  );
};

export default ChatPane; 