/**
 * Controls Component - Redesigned with Settings and Authentication
 * 
 * Minimal icon-based controls for writing preferences and settings.
 * Now includes theme settings and authentication access.
 */

import React, { useState, useEffect, useRef } from 'react';
import { useAppContext } from '../contexts/AppContext';
import { useAuth } from '../contexts/AuthContext';
import AuthModal from './AuthModal';
import UserProfileModal from './UserProfileModal';

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

  const { isAuthenticated, user, logout } = useAuth();

  const [activeDropdown, setActiveDropdown] = useState<string | null>(null);
  const [timerActive, setTimerActive] = useState(false);
  const containerRef = useRef<HTMLDivElement>(null);
  const [showAuthModal, setShowAuthModal] = useState(false);
  const [authMode, setAuthMode] = useState<'signin' | 'signup'>('signin');
  const [showProfileModal, setShowProfileModal] = useState(false);

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
      case 'timer':
        if (value === 'toggle') {
          setTimerActive(!timerActive);
        }
        break;
      case 'save':
        if (value === 'checkpoint') {
          handleSaveCheckpoint();
        }
        break;
      case 'settings':
        // Handle settings options here
        console.log('Settings option:', value);
        break;
      case 'auth':
        switch (value) {
          case 'login':
            setAuthMode('signin');
            setShowAuthModal(true);
            break;
          case 'register':
            setAuthMode('signup');
            setShowAuthModal(true);
            break;
          case 'profile':
            setShowProfileModal(true);
            break;
          case 'logout':
            logout();
            break;
          default:
            break;
        }
        break;
    }
    setActiveDropdown(null);
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
        <div className="control-icon-group">
          <button
            className={`control-icon-button ${activeDropdown === 'timer' ? 'active' : ''} ${timerActive ? 'authenticated' : ''}`}
            onClick={() => toggleDropdown('timer')}
            title="Writing Timer Options"
            aria-expanded={activeDropdown === 'timer'}
            aria-haspopup="true"
          >
            <div className="control-button-content">
              <span className="control-icon">⏱️</span>
            </div>
            <div className="control-tooltip">Timer</div>
          </button>
          {activeDropdown === 'timer' && (
            <div className="control-dropdown expanded-dropdown" role="menu">
              <div className="dropdown-header">Writing Timer</div>
              <button
                className={`dropdown-option ${timerActive ? 'selected' : ''}`}
                onClick={() => handleSelection('timer', 'toggle')}
                role="menuitem"
              >
                <span className="option-icon">⏱️</span>
                <span className="option-text">{timerActive ? 'Stop Timer' : 'Start Timer'}</span>
                {timerActive && <span className="selected-indicator">✓</span>}
              </button>
              <button
                className="dropdown-option"
                onClick={() => handleSelection('timer', 'reset')}
                role="menuitem"
              >
                <span className="option-icon">🔄</span>
                <span className="option-text">Reset Timer</span>
              </button>
              <button
                className="dropdown-option"
                onClick={() => handleSelection('timer', 'settings')}
                role="menuitem"
              >
                <span className="option-icon">⚙️</span>
                <span className="option-text">Timer Settings</span>
              </button>
            </div>
          )}
        </div>

        {/* Save Checkpoint Button */}
        <div className="control-icon-group">
          <button
            className={`control-icon-button ${activeDropdown === 'save' ? 'active' : ''}`}
            onClick={() => toggleDropdown('save')}
            title="Save Options"
            aria-expanded={activeDropdown === 'save'}
            aria-haspopup="true"
          >
            <div className="control-button-content">
              <span className="control-icon">💾</span>
            </div>
            <div className="control-tooltip">Save</div>
          </button>
          {activeDropdown === 'save' && (
            <div className="control-dropdown expanded-dropdown" role="menu">
              <div className="dropdown-header">Save Options</div>
              <button
                className="dropdown-option"
                onClick={() => handleSelection('save', 'checkpoint')}
                role="menuitem"
              >
                <span className="option-icon">💾</span>
                <span className="option-text">Save Checkpoint</span>
              </button>
              <button
                className="dropdown-option"
                onClick={() => handleSelection('save', 'auto')}
                role="menuitem"
              >
                <span className="option-icon">🔄</span>
                <span className="option-text">Auto-Save Settings</span>
              </button>
              <button
                className="dropdown-option"
                onClick={() => handleSelection('save', 'export')}
                role="menuitem"
              >
                <span className="option-icon">📤</span>
                <span className="option-text">Export Document</span>
              </button>
            </div>
          )}
        </div>

        {/* Settings Icon */}
        <div className="control-icon-group">
          <button
            className={`control-icon-button ${activeDropdown === 'settings' ? 'active' : ''}`}
            onClick={() => toggleDropdown('settings')}
            title="Settings Options"
            aria-expanded={activeDropdown === 'settings'}
            aria-haspopup="true"
          >
            <div className="control-button-content">
              <span className="control-icon">⚙️</span>
            </div>
            <div className="control-tooltip">Settings</div>
          </button>
          {activeDropdown === 'settings' && (
            <div className="control-dropdown expanded-dropdown" role="menu">
              <div className="dropdown-header">Settings</div>
              <button
                className="dropdown-option"
                onClick={() => handleSelection('settings', 'preferences')}
                role="menuitem"
              >
                <span className="option-icon">🎨</span>
                <span className="option-text">Preferences</span>
              </button>
              <button
                className="dropdown-option"
                onClick={() => handleSelection('settings', 'theme')}
                role="menuitem"
              >
                <span className="option-icon">🌙</span>
                <span className="option-text">Theme Settings</span>
              </button>
              <button
                className="dropdown-option"
                onClick={() => handleSelection('settings', 'keyboard')}
                role="menuitem"
              >
                <span className="option-icon">⌨️</span>
                <span className="option-text">Keyboard Shortcuts</span>
              </button>
            </div>
          )}
        </div>

        {/* Sign In/Sign Up Icon */}
        <div className="control-icon-group">
          <button
            className={`control-icon-button ${activeDropdown === 'auth' ? 'active' : ''} ${isAuthenticated ? 'authenticated' : ''}`}
            onClick={() => toggleDropdown('auth')}
            title={isAuthenticated ? `Account: ${user?.display_name || user?.username}` : "Account Options"}
            aria-expanded={activeDropdown === 'auth'}
            aria-haspopup="true"
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
              {isAuthenticated ? "Account" : "Sign In/Up"}
            </div>
          </button>
          {activeDropdown === 'auth' && (
            <div className="control-dropdown expanded-dropdown" role="menu">
              <div className="dropdown-header">{isAuthenticated ? 'Account' : 'Authentication'}</div>
              {isAuthenticated ? (
                <>
                  <button
                    className="dropdown-option"
                    onClick={() => handleSelection('auth', 'profile')}
                    role="menuitem"
                  >
                    <span className="option-icon">👤</span>
                    <span className="option-text">View Profile</span>
                  </button>
                  <button
                    className="dropdown-option"
                    onClick={() => handleSelection('auth', 'settings')}
                    role="menuitem"
                  >
                    <span className="option-icon">⚙️</span>
                    <span className="option-text">Account Settings</span>
                  </button>
                  <button
                    className="dropdown-option"
                    onClick={() => handleSelection('auth', 'logout')}
                    role="menuitem"
                  >
                    <span className="option-icon">🚪</span>
                    <span className="option-text">Sign Out</span>
                  </button>
                </>
              ) : (
                <>
                  <button
                    className="dropdown-option"
                    onClick={() => handleSelection('auth', 'login')}
                    role="menuitem"
                  >
                    <span className="option-icon">🔑</span>
                    <span className="option-text">Sign In</span>
                  </button>
                  <button
                    className="dropdown-option"
                    onClick={() => handleSelection('auth', 'register')}
                    role="menuitem"
                  >
                    <span className="option-icon">📝</span>
                    <span className="option-text">Sign Up</span>
                  </button>
                </>
              )}
            </div>
          )}
        </div>
      </div>

      {/* Authentication Modal */}
      <AuthModal
        isOpen={showAuthModal}
        onClose={() => setShowAuthModal(false)}
        initialMode={authMode}
      />

      {/* User Profile Modal */}
      <UserProfileModal
        isOpen={showProfileModal}
        onClose={() => setShowProfileModal(false)}
      />
    </div>
  );
};

export default Controls; 