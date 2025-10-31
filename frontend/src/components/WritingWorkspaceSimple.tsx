/**
 * WritingWorkspace - Simple, competition-focused version
 *
 * Features:
 * - TipTap editor for writing
 * - Auto voice consistency analysis (like Grammarly)
 * - Red wavy underlines on inconsistent dialogue
 * - Character profiles panel
 * - Optional backend integration
 */

import React, { useState, useEffect, useMemo, useCallback } from 'react';
import { useEditor, EditorContent } from '@tiptap/react';
import StarterKit from '@tiptap/starter-kit';
import { geminiService } from '../services/gemini.service';
import { voiceAPI } from '../services/api.service';
import '../styles/workspace.css';

interface VoiceResult {
  character_name: string;
  is_consistent: boolean;
  confidence_score: number;
  voice_traits: {
    formality?: string;
    vocabulary?: string;
    tone?: string;
    complexity?: string;
  };
  issues: string[];
  suggestions: string[];
  flagged_text?: string;
}

interface CharacterProfile {
  name: string;
  consistency: number;
  traits: Record<string, string>;
  dialogueCount: number;
}

// NOTE: Dialogue extraction now uses Gemini AI (see analyzeVoice function)
// This is much smarter than regex and catches all dialogue formats!

// Debounce helper
const debounce = <T extends (...args: any[]) => any>(
  func: T,
  wait: number
): ((...args: Parameters<T>) => void) => {
  let timeout: NodeJS.Timeout;
  return (...args: Parameters<T>) => {
    clearTimeout(timeout);
    timeout = setTimeout(() => func(...args), wait);
  };
};

export const WritingWorkspace: React.FC = () => {
  const [apiKey, setApiKey] = useState('');
  const [isInitialized, setIsInitialized] = useState(false);
  const [voiceResults, setVoiceResults] = useState<VoiceResult[]>([]);
  const [characterProfiles, setCharacterProfiles] = useState<CharacterProfile[]>([]);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [wordCount, setWordCount] = useState(0);
  const [showApiKeyInput, setShowApiKeyInput] = useState(false);

  // Load API key from localStorage
  useEffect(() => {
    const savedKey = localStorage.getItem('gemini_api_key');
    if (savedKey) {
      setApiKey(savedKey);
      geminiService.initialize(savedKey);
      setIsInitialized(true);
    } else {
      setShowApiKeyInput(true);
    }
  }, []);

  // Initialize Gemini
  const handleInitialize = () => {
    if (!apiKey.trim()) {
      alert('Please enter a valid API key');
      return;
    }

    try {
      geminiService.initialize(apiKey);
      localStorage.setItem('gemini_api_key', apiKey);
      setIsInitialized(true);
      setShowApiKeyInput(false);
    } catch (err) {
      alert('Failed to initialize Gemini API');
    }
  };

  // TipTap editor
  const editor = useEditor({
    extensions: [StarterKit],
    content: localStorage.getItem('document_content') || '<p>Start writing your story here...</p>',
    editorProps: {
      attributes: {
        class: 'prose prose-lg focus:outline-none min-h-screen p-8',
      },
    },
    onUpdate: ({ editor }) => {
      const text = editor.getText();
      const html = editor.getHTML();

      // Save to localStorage
      localStorage.setItem('document_content', html);

      // Update word count
      const words = text.trim().split(/\s+/).filter(w => w.length > 0).length;
      setWordCount(words);

      // Auto-analyze after 2 seconds of no typing
      if (isInitialized) {
        debouncedAnalyze(text);
      }
    },
  });

  // Auto voice analysis
  const analyzeVoice = useCallback(async (text: string) => {
    if (!text || text.length < 50) return;

    setIsAnalyzing(true);

    try {
      // Extract dialogue using Gemini AI (much smarter than regex!)
      console.log('🔍 Extracting dialogue with Gemini...');
      const dialogues = await geminiService.extractDialogue(text);

      if (dialogues.length === 0) {
        console.log('ℹ️ No dialogue found in text');
        setIsAnalyzing(false);
        return;
      }

      console.log(`📝 Found ${dialogues.length} dialogue pieces:`, dialogues);

      // Analyze with Gemini
      const results = await geminiService.analyzeDialogueConsistency(dialogues);

      console.log('✅ Analysis results:', results);

      setVoiceResults(results);

      // Build character profiles
      const profiles: CharacterProfile[] = results.map(result => ({
        name: result.character_name,
        consistency: result.confidence_score * 100,
        traits: result.voice_traits,
        dialogueCount: dialogues.filter(d => d.speaker === result.character_name).length,
      }));

      setCharacterProfiles(profiles);

      // TODO: Add underlines to editor for inconsistent dialogues
      // This requires creating a custom TipTap extension

    } catch (error) {
      console.error('❌ Voice analysis failed:', error);
    } finally {
      setIsAnalyzing(false);
    }
  }, [isInitialized]);

  // Debounced version
  const debouncedAnalyze = useMemo(
    () => debounce(analyzeVoice, 2000),
    [analyzeVoice]
  );

  // API key input screen
  if (showApiKeyInput) {
    return (
      <div className="api-key-screen">
        <div className="api-key-card">
          <h1>Owen - Voice Consistency Checker</h1>
          <p>Enter your Gemini API key to get started</p>
          <input
            type="text"
            value={apiKey}
            onChange={(e) => setApiKey(e.target.value)}
            placeholder="AIza..."
            className="api-key-input"
          />
          <button onClick={handleInitialize} className="btn-primary">
            Initialize
          </button>
          <p className="api-key-help">
            Get your API key from: <a href="https://makersuite.google.com/app/apikey" target="_blank" rel="noopener noreferrer">Google AI Studio</a>
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="workspace">
      {/* Header */}
      <div className="workspace-header">
        <div className="header-left">
          <h1>Owen</h1>
          <span className="subtitle">Voice Consistency Checker</span>
        </div>
        <div className="header-right">
          <span className="word-count">{wordCount} words</span>
          {isAnalyzing && <span className="analyzing">Analyzing...</span>}
          <button
            onClick={() => {
              localStorage.removeItem('gemini_api_key');
              setShowApiKeyInput(true);
              setIsInitialized(false);
            }}
            className="btn-secondary"
          >
            Change API Key
          </button>
        </div>
      </div>

      {/* Main Content */}
      <div className="workspace-content">
        {/* Editor Panel */}
        <div className="editor-panel">
          <EditorContent editor={editor} />
        </div>

        {/* Voice Analysis Panel */}
        <div className="voice-panel">
          <h3>Character Profiles</h3>

          {characterProfiles.length === 0 ? (
            <div className="empty-state">
              <p>Start writing dialogue to see character profiles!</p>
              <p className="empty-hint">Example:</p>
              <pre className="example-code">
                Jake: "Listen up. Move!"
                Emma: "But what about—"
                Jake: "I said move!"
              </pre>
            </div>
          ) : (
            <div className="profiles-list">
              {characterProfiles.map(profile => (
                <div key={profile.name} className="profile-card">
                  <div className="profile-header">
                    <h4>{profile.name}</h4>
                    <span className={`consistency-badge ${profile.consistency >= 80 ? 'high' : profile.consistency >= 60 ? 'medium' : 'low'}`}>
                      {profile.consistency.toFixed(0)}%
                    </span>
                  </div>

                  <div className="profile-traits">
                    {Object.entries(profile.traits).map(([key, value]) => (
                      <div key={key} className="trait">
                        <span className="trait-label">{key}:</span>
                        <span className="trait-value">{value}</span>
                      </div>
                    ))}
                  </div>

                  <div className="profile-stats">
                    <span className="dialogue-count">{profile.dialogueCount} dialogue{profile.dialogueCount !== 1 ? 's' : ''}</span>
                  </div>
                </div>
              ))}
            </div>
          )}

          {/* Voice Issues */}
          {voiceResults.some(r => !r.is_consistent) && (
            <div className="voice-issues">
              <h3>⚠️ Voice Inconsistencies</h3>
              {voiceResults
                .filter(r => !r.is_consistent)
                .map((result, i) => (
                  <div key={i} className="issue-card">
                    <h4>{result.character_name}</h4>
                    <ul className="issues-list">
                      {result.issues.map((issue, j) => (
                        <li key={j}>{issue}</li>
                      ))}
                    </ul>
                    {result.suggestions.length > 0 && (
                      <>
                        <h5>Suggestions:</h5>
                        <ul className="suggestions-list">
                          {result.suggestions.map((suggestion, j) => (
                            <li key={j}>{suggestion}</li>
                          ))}
                        </ul>
                      </>
                    )}
                  </div>
                ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default WritingWorkspace;
