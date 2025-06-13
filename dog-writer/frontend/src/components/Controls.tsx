/**
 * Controls Component - Redesigned with Settings and Authentication
 * 
 * Minimal icon-based controls for writing preferences and settings.
 * Now includes theme settings and authentication access.
 */

import React, { useState, useEffect, useRef } from 'react';
import { useAppContext } from '../contexts/AppContext';
import { useAuth } from '../contexts/AuthContext';
import SettingsModal from './SettingsModal';
import AuthModal from './AuthModal';

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

  const { isAuthenticated, user } = useAuth();

  const [activeDropdown, setActiveDropdown] = useState<string | null>(null);
  const [timerActive, setTimerActive] = useState(false);
  const [showSettingsModal, setShowSettingsModal] = useState(false);
  const [showAuthModal, setShowAuthModal] = useState(false);
  const [authMode, setAuthMode] = useState<'login' | 'register'>('login');
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

  const handleAuthClick = () => {
    if (isAuthenticated) {
      // If authenticated, show settings modal (profile will be in settings)
      setShowSettingsModal(true);
    } else {
      // If not authenticated, show auth modal
      setAuthMode('login');
      setShowAuthModal(true);
    }
  };

  const handleSettingsClick = () => {
    setShowSettingsModal(true);
  };

  return (
    <div className={`controls-container ${activeDropdown ? 'expanded' : ''}`} ref={containerRef}>
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
            <div className="control-dropdown expanded-dropdown" role="menu">
              <div className="dropdown-header">Choose Author Persona</div>
              {authorPersonas.map((persona) => (
                <button
                  key={persona}
                  className={`dropdown-option ${authorPersona === persona ? 'selected' : ''}`}
                  onClick={() => handleSelection('persona', persona)}
                  role="menuitem"
                >
                  <span className="option-icon">✍️</span>
                  <span className="option-text">{persona}</span>
                  {authorPersona === persona && <span className="selected-indicator">✓</span>}
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
            <div className="control-dropdown expanded-dropdown" role="menu">
              <div className="dropdown-header">Writing Focus</div>
              {helpFocuses.map((focus) => (
                <button
                  key={focus}
                  className={`dropdown-option ${helpFocus === focus ? 'selected' : ''}`}
                  onClick={() => handleSelection('focus', focus)}
                  role="menuitem"
                >
                  <span className="option-icon">🎯</span>
                  <span className="option-text">{focus}</span>
                  {helpFocus === focus && <span className="selected-indicator">✓</span>}
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
            <div className="control-dropdown expanded-dropdown" role="menu">
              <div className="dropdown-header">English Variant</div>
              {englishVariants.map((variant) => (
                <button
                  key={variant.value}
                  className={`dropdown-option ${userPreferences.english_variant === variant.value ? 'selected' : ''}`}
                  onClick={() => handleSelection('english', variant.value)}
                  role="menuitem"
                >
                  <span className="option-icon">🌍</span>
                  <span className="option-text">{variant.label}</span>
                  {userPreferences.english_variant === variant.value && <span className="selected-indicator">✓</span>}
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
            <div className="control-dropdown expanded-dropdown" role="menu">
              <div className="dropdown-header">AI Model</div>
              {llmOptions.map((model) => (
                <button
                  key={model}
                  className={`dropdown-option ${selectedLLM === model ? 'selected' : ''}`}
                  onClick={() => handleSelection('model', model)}
                  role="menuitem"
                >
                  <span className="option-icon">🤖</span>
                  <span className="option-text">{model}</span>
                  {selectedLLM === model && <span className="selected-indicator">✓</span>}
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

        {/* NEW: Settings Icon */}
        <div className="control-action-group">
          <button
            className="control-action-button"
            onClick={handleSettingsClick}
            title="Settings"
            aria-label="Settings"
          >
            <div className="control-button-content">
              <span className="control-icon">⚙️</span>
            </div>
            <div className="control-tooltip">Settings</div>
          </button>
        </div>

        {/* NEW: Sign In/Sign Up Icon */}
        <div className="control-action-group">
          <button
            className={`control-action-button ${isAuthenticated ? 'authenticated' : ''}`}
            onClick={handleAuthClick}
            title={isAuthenticated ? `Signed in as ${user?.display_name || user?.username}` : "Sign In/Up"}
            aria-label={isAuthenticated ? "User Profile" : "Sign In/Up"}
          >
            <div className="control-button-content">
              {isAuthenticated ? (
                <span className="control-icon user-avatar">
                  {(user?.display_name || user?.username || 'U').charAt(0).toUpperCase()}
                </span>
              ) : (
                <span className="control-icon">👤</span>
              )}
            </div>
            <div className="control-tooltip">
              {isAuthenticated ? "Profile" : "Sign In/Up"}
            </div>
          </button>
        </div>
      </div>

      {/* Settings Modal */}
      <SettingsModal
        isOpen={showSettingsModal}
        onClose={() => setShowSettingsModal(false)}
      />

      {/* Authentication Modal */}
      <AuthModal
        isOpen={showAuthModal}
        onClose={() => setShowAuthModal(false)}
        initialMode={authMode}
      />
    </div>
  );
};

export default Controls; 