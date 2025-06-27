/**
 * ChatPane Component - Clean Architecture Implementation
 * 
 * REFACTORED using Atomic Design principles:
 * - Single Responsibility: Coordinate chat workflow
 * - Delegates specific responsibilities to focused sub-components
 * - Uses composition over complex state management
 * - Follows React best practices for maintainability
 */

import React, { useState, useCallback, useEffect } from 'react';
import { EnhancedChatInput } from './chat-interface/EnhancedChatInput';
import { ThinkingTrail } from './chat/ThinkingTrail';
import { 
  ChatHeader,
  MessagesContainer,
  generateContextualPrompts
} from './chat-interface';
import { logger } from '../utils/logger';
import { useChatContext } from '../contexts/ChatContext';

/**
 * Template Component: ChatPane
 * 
 * CLEAN ARCHITECTURE IMPLEMENTATION:
 * - Single Responsibility: Coordinate chat interface workflow
 * - Delegates UI rendering to focused sub-components
 * - Manages business logic coordination
 * - Handles event orchestration between components
 * 
 * RESPONSIBILITIES:
 * 1. State coordination between sub-components
 * 2. Business logic orchestration (message handling, prompts)
 * 3. Event handling coordination
 * 4. Context integration
 */
const ChatPane: React.FC = () => {
  const {
    messages,
    handleSendMessage,
    thinkingTrail,
    isStreaming,
    streamText,
    isThinking,
    chatApiError,
    apiGlobalError,
    checkApiConnection,
    // Chat settings
    authorPersona,
    setAuthorPersona,
    helpFocus,
    setHelpFocus,
    selectedLLM,
    setSelectedLLM,
    // AI interaction mode
    aiMode,
    setAiMode,
    // Text highlighting
    highlightedText,
    // CRITICAL FIX: Add suggestions state from context
    currentSuggestions,
    clearSuggestions,
  } = useChatContext();

  const [showThinkingTrail, setShowThinkingTrail] = useState(false);

  // Business Logic: Generate contextual prompts for highlighted text
  const contextualPrompts = useCallback(() => {
    if (!highlightedText) return [];
    return generateContextualPrompts(authorPersona, helpFocus);
  }, [highlightedText, authorPersona, helpFocus]);

  // Event Handler: Send message with highlighted text context
  const handleSendMessageWrapper = useCallback((message: string) => {
    let finalMessage = message;
    
    // Include highlighted text context if available and not already included
    if (highlightedText && !message.includes(highlightedText)) {
      finalMessage = `${message}\n\nSelected text: "${highlightedText}"`;
    }
    
    handleSendMessage(finalMessage);
  }, [highlightedText, handleSendMessage]);

  // Note: handleGetOptions removed - EnhancedChatInput handles suggestions internally

  // Event Handler: Handle quick question prompts
  const handlePromptClick = useCallback((prompt: string) => {
    let finalMessage = prompt;
    
    // Include highlighted text context if available
    if (highlightedText) {
      finalMessage = `${prompt}\n\nSelected text: "${highlightedText}"`;
    }
    
    handleSendMessageWrapper(finalMessage);
  }, [highlightedText, handleSendMessageWrapper]);

  // Event Handler: Test API connection
  const handleTestConnection = useCallback(async () => {
    try {
      await checkApiConnection();
      let testMessage = "Test connection - please respond with a simple greeting.";
      
      // Include highlighted text context in test if available
      if (highlightedText) {
        testMessage += `\n\nSelected text for context: "${highlightedText}"`;
      }
      
      handleSendMessageWrapper(testMessage);
    } catch (error) {
      logger.error('Connection test failed:', error);
    }
  }, [checkApiConnection, handleSendMessageWrapper, highlightedText]);

  // Event Handler: Toggle thinking trail visibility
  const toggleThinkingTrail = useCallback(() => {
    setShowThinkingTrail(prev => !prev);
  }, []);

  // Effect: Handle automatic message sending from highlighted text (legacy support)
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
      {/* Chat Header with Controls - Molecular Component */}
      <ChatHeader
        authorPersona={authorPersona}
        helpFocus={helpFocus}
        selectedLLM={selectedLLM}
        aiMode={aiMode}
        onAuthorPersonaChange={setAuthorPersona}
        onHelpFocusChange={setHelpFocus}
        onLLMChange={setSelectedLLM}
        onAiModeChange={setAiMode}
      />
      
      {/* Messages Container - Organism Component */}
      <MessagesContainer
        messages={messages}
        highlightedText={highlightedText}
        contextualPrompts={contextualPrompts()}
        chatApiError={chatApiError}
        apiGlobalError={apiGlobalError}
        streamText={streamText}
        isStreaming={isStreaming}
        onPromptClick={handlePromptClick}
        onTestConnection={handleTestConnection}
        // CRITICAL FIX: Pass suggestions state to MessagesContainer
        currentSuggestions={currentSuggestions}
        clearSuggestions={clearSuggestions}
      />

      {/* Thinking Trail - Existing Component */}
      <ThinkingTrail 
        trail={thinkingTrail || undefined}
        isThinking={isThinking}
        isVisible={showThinkingTrail}
        onToggleVisibility={toggleThinkingTrail}
      />

      {/* CRITICAL FIX: Replace ChatInput with EnhancedChatInput */}
      <EnhancedChatInput 
        onSendMessage={handleSendMessageWrapper}
        isLoading={isStreaming || isThinking}
        placeholder="Ask Owen anything about your writing..."
      />
    </div>
  );
};

export default ChatPane; 