/**
 * Controls Component - Redesigned
 * 
 * Minimal icon-based controls for writing preferences and settings.
 * Uses the new design system for consistent styling.
 */

import React, { useState, useEffect, useRef } from 'react';
import { useAppContext } from '../contexts/AppContext';

const Controls: React.FC = () => {
  const {
    authorPersona,
    setAuthorPersona,
    helpFocus,
    setHelpFocus,
    selectedLLM,
    setSelectedLLM,
    handleSaveCheckpoint,
    userPreferences,
    englishVariants,
    updateEnglishVariant
  } = useAppContext();

  const [activeDropdown, setActiveDropdown] = useState<string | null>(null);
  const [timerActive, setTimerActive] = useState(false);
  const containerRef = useRef<HTMLDivElement>(null);

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (containerRef.current && !containerRef.current.contains(event.target as Node)) {
        setActiveDropdown(null);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, []);

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

  const toggleDropdown = (dropdown: string) => {
    setActiveDropdown(activeDropdown === dropdown ? null : dropdown);
  };

  const handleSelection = (dropdown: string, value: string) => {
    switch (dropdown) {
      case 'persona':
        setAuthorPersona(value);
        break;
      case 'focus':
        setHelpFocus(value);
        break;
      case 'english':
        updateEnglishVariant(value);
        break;
      case 'model':
        setSelectedLLM(value);
        break;
    }
    setActiveDropdown(null);
  };

  const getDisplayValue = (type: string) => {
    switch (type) {
      case 'persona':
        return authorPersona.split(' ')[0]; // First name only
      case 'focus':
        return helpFocus.split(' ')[0]; // First word only
      case 'english':
        const variant = englishVariants.find(v => v.value === userPreferences.english_variant);
        return variant?.label.split(' ')[0] || 'US'; // First word only
      case 'model':
        return selectedLLM.split(' ')[0]; // First word only
      default:
        return '';
    }
  };

  const handleTimerToggle = () => {
    setTimerActive(!timerActive);
    // Here you could integrate with the actual writing timer functionality
  };

  return (
    <div className="controls-container" ref={containerRef}>
      <div className="controls-left">
        
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
            <div className="control-tooltip">Author</div>
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
            <div className="control-tooltip">Focus</div>
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

        {/* English Style */}
        <div className="control-icon-group">
          <button
            className={`control-icon-button ${activeDropdown === 'english' ? 'active' : ''}`}
            onClick={() => toggleDropdown('english')}
            title={`English Style: ${englishVariants.find(v => v.value === userPreferences.english_variant)?.label}`}
            aria-expanded={activeDropdown === 'english'}
            aria-haspopup="true"
          >
            <div className="control-button-content">
              <span className="control-icon">🌍</span>
            </div>
            <div className="control-tooltip">English</div>
          </button>
          {activeDropdown === 'english' && (
            <div className="control-dropdown" role="menu">
              {englishVariants.map((variant) => (
                <button
                  key={variant.value}
                  className={`dropdown-option ${userPreferences.english_variant === variant.value ? 'selected' : ''}`}
                  onClick={() => handleSelection('english', variant.value)}
                  role="menuitem"
                >
                  {variant.label}
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
            <div className="control-tooltip">AI Model</div>
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

        {/* Divider */}
        <div className="controls-divider"></div>

        {/* Writing Timer Clock Icon */}
        <div className="control-action-group">
          <button
            className={`control-action-button ${timerActive ? 'active' : ''}`}
            onClick={handleTimerToggle}
            title={timerActive ? "Stop Writing Timer" : "Start Writing Timer"}
            aria-label={timerActive ? "Stop Writing Timer" : "Start Writing Timer"}
          >
            <div className="control-button-content">
              <span className="control-icon">⏱️</span>
            </div>
            <div className="control-tooltip">Timer</div>
          </button>
        </div>

        {/* Save Checkpoint Button */}
        <div className="control-action-group">
          <button
            className="control-action-button"
            onClick={handleSaveCheckpoint}
            title="Save Checkpoint"
            aria-label="Save Checkpoint"
          >
            <div className="control-button-content">
              <span className="control-icon">💾</span>
            </div>
            <div className="control-tooltip">Save</div>
          </button>
        </div>
      </div>
    </div>
  );
};

export default Controls; 