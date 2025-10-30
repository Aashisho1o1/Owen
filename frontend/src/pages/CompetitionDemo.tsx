/**
 * Competition Demo Page
 *
 * Focused, competition-winning features:
 * 1. Dialogue Consistency Checker
 * 2. Classic Author Feedback
 * 3. Writing Help Categorization
 *
 * Chrome Built-in AI Challenge 2025
 * Strategy: Simple, focused, impressive
 */

import React, { useState, useEffect } from 'react';
import { geminiService, DialogueAnalysisResult, AuthorFeedback, WritingHelpCategory } from '../services/gemini.service';
import './CompetitionDemo.css';

type Feature = 'dialogue' | 'author' | 'categorize';

const SAMPLE_DIALOGUES = {
  consistent: [
    { speaker: "Jake", text: "Listen up. We got five minutes. You're with me or you're not." },
    { speaker: "Jake", text: "No time for questions. Move." },
    { speaker: "Jake", text: "I said move! Now!" },
  ],
  inconsistent: [
    { speaker: "Emma", text: "Hey! Like, we should totally go to the mall later!" },
    { speaker: "Emma", text: "I must express my profound disagreement with your proposition regarding our afternoon activities." },
    { speaker: "Emma", text: "Whatever, dude. Let's just chill." },
  ],
};

const SAMPLE_TEXT_FOR_AUTHOR = `The old man sat by the water. The sun was hot. He watched the line. He had been there since morning. The fish would come or they would not come. That was how it was.`;

const CLASSIC_AUTHORS = [
  'Hemingway',
  'Jane Austen',
  'Stephen King',
  'Toni Morrison',
  'Raymond Carver',
];

export const CompetitionDemo: React.FC = () => {
  const [apiKey, setApiKey] = useState('');
  const [isInitialized, setIsInitialized] = useState(false);
  const [activeFeature, setActiveFeature] = useState<Feature>('dialogue');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Dialogue state
  const [dialogues, setDialogues] = useState<Array<{ speaker: string; text: string }>>([
    { speaker: '', text: '' },
  ]);
  const [dialogueResults, setDialogueResults] = useState<DialogueAnalysisResult[] | null>(null);

  // Author feedback state
  const [authorText, setAuthorText] = useState('');
  const [selectedAuthor, setSelectedAuthor] = useState('Hemingway');
  const [authorFeedback, setAuthorFeedback] = useState<AuthorFeedback | null>(null);

  // Categorization state
  const [categorizeText, setCategorizeText] = useState('');
  const [category, setCategory] = useState<WritingHelpCategory | null>(null);

  // Initialize Gemini on mount if API key in localStorage
  useEffect(() => {
    const savedKey = localStorage.getItem('gemini_api_key');
    if (savedKey) {
      setApiKey(savedKey);
      geminiService.initialize(savedKey);
      setIsInitialized(true);
    }
  }, []);

  const handleInitialize = () => {
    if (!apiKey.trim()) {
      setError('Please enter a valid API key');
      return;
    }

    try {
      geminiService.initialize(apiKey);
      localStorage.setItem('gemini_api_key', apiKey);
      setIsInitialized(true);
      setError(null);
    } catch (err) {
      setError('Failed to initialize Gemini API');
    }
  };

  const loadSampleDialogue = (type: 'consistent' | 'inconsistent') => {
    setDialogues(SAMPLE_DIALOGUES[type]);
    setDialogueResults(null);
  };

  const addDialogue = () => {
    setDialogues([...dialogues, { speaker: '', text: '' }]);
  };

  const updateDialogue = (index: number, field: 'speaker' | 'text', value: string) => {
    const updated = [...dialogues];
    updated[index][field] = value;
    setDialogues(updated);
  };

  const removeDialogue = (index: number) => {
    if (dialogues.length > 1) {
      setDialogues(dialogues.filter((_, i) => i !== index));
    }
  };

  const analyzeDialogues = async () => {
    const validDialogues = dialogues.filter(d => d.speaker.trim() && d.text.trim());

    if (validDialogues.length === 0) {
      setError('Please add at least one dialogue');
      return;
    }

    setIsLoading(true);
    setError(null);
    setDialogueResults(null);

    try {
      const results = await geminiService.analyzeDialogueConsistency(validDialogues);
      setDialogueResults(results);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Analysis failed');
    } finally {
      setIsLoading(false);
    }
  };

  const getAuthorFeedback = async () => {
    if (!authorText.trim()) {
      setError('Please enter some text');
      return;
    }

    setIsLoading(true);
    setError(null);
    setAuthorFeedback(null);

    try {
      const feedback = await geminiService.getClassicAuthorFeedback(
        authorText,
        selectedAuthor,
        true
      );
      setAuthorFeedback(feedback);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Analysis failed');
    } finally {
      setIsLoading(false);
    }
  };

  const categorizeWriting = async () => {
    if (!categorizeText.trim()) {
      setError('Please enter some text');
      return;
    }

    setIsLoading(true);
    setError(null);
    setCategory(null);

    try {
      const result = await geminiService.categorizeWritingHelp(categorizeText);
      setCategory(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Analysis failed');
    } finally {
      setIsLoading(false);
    }
  };

  // API Key Setup Screen
  if (!isInitialized) {
    return (
      <div className="competition-demo">
        <div className="setup-screen">
          <div className="setup-card">
            <h1>🎯 Owen - Voice Consistency Analyzer</h1>
            <p className="subtitle">Chrome Built-in AI Challenge 2025</p>

            <div className="feature-badges">
              <span className="badge">✅ Dialogue Consistency Checker</span>
              <span className="badge">✅ Classic Author Feedback</span>
              <span className="badge">✅ Writing Help Categorization</span>
            </div>

            <div className="setup-form">
              <label>Google Gemini API Key</label>
              <input
                type="password"
                value={apiKey}
                onChange={(e) => setApiKey(e.target.value)}
                placeholder="Enter your Gemini API key"
                className="api-key-input"
              />
              <button onClick={handleInitialize} className="btn-primary">
                Initialize Owen
              </button>

              <div className="help-text">
                <p>Don't have an API key? <a href="https://makersuite.google.com/app/apikey" target="_blank" rel="noopener noreferrer">Get one free</a></p>
                <p className="privacy">🔒 Your API key is stored locally and never sent to our servers</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  // Main App
  return (
    <div className="competition-demo">
      <header className="demo-header">
        <h1>Owen Voice Analyzer</h1>
        <p>Powered by Google Gemini API</p>
      </header>

      {/* Feature Tabs */}
      <div className="feature-tabs">
        <button
          className={`tab ${activeFeature === 'dialogue' ? 'active' : ''}`}
          onClick={() => setActiveFeature('dialogue')}
        >
          💬 Dialogue Consistency
        </button>
        <button
          className={`tab ${activeFeature === 'author' ? 'active' : ''}`}
          onClick={() => setActiveFeature('author')}
        >
          📚 Classic Author Feedback
        </button>
        <button
          className={`tab ${activeFeature === 'categorize' ? 'active' : ''}`}
          onClick={() => setActiveFeature('categorize')}
        >
          🎯 Writing Help
        </button>
      </div>

      {/* Error Display */}
      {error && (
        <div className="error-banner">
          {error}
        </div>
      )}

      {/* Feature 1: Dialogue Consistency */}
      {activeFeature === 'dialogue' && (
        <div className="feature-section">
          <div className="section-header">
            <h2>Dialogue Consistency Checker</h2>
            <p>Analyze character dialogue for voice consistency</p>
          </div>

          <div className="sample-buttons">
            <button onClick={() => loadSampleDialogue('consistent')} className="btn-sample">
              Load Consistent Example
            </button>
            <button onClick={() => loadSampleDialogue('inconsistent')} className="btn-sample">
              Load Inconsistent Example
            </button>
          </div>

          <div className="dialogue-inputs">
            {dialogues.map((dialogue, index) => (
              <div key={index} className="dialogue-row">
                <input
                  type="text"
                  placeholder="Speaker name"
                  value={dialogue.speaker}
                  onChange={(e) => updateDialogue(index, 'speaker', e.target.value)}
                  className="speaker-input"
                />
                <textarea
                  placeholder="What they say..."
                  value={dialogue.text}
                  onChange={(e) => updateDialogue(index, 'text', e.target.value)}
                  className="dialogue-input"
                  rows={2}
                />
                {dialogues.length > 1 && (
                  <button onClick={() => removeDialogue(index)} className="btn-remove">
                    ✕
                  </button>
                )}
              </div>
            ))}
          </div>

          <div className="action-buttons">
            <button onClick={addDialogue} className="btn-secondary">
              + Add Dialogue
            </button>
            <button
              onClick={analyzeDialogues}
              disabled={isLoading}
              className="btn-primary"
            >
              {isLoading ? 'Analyzing...' : 'Analyze Consistency'}
            </button>
          </div>

          {/* Dialogue Results */}
          {dialogueResults && (
            <div className="results-section">
              <h3>Analysis Results</h3>
              {dialogueResults.map((result, index) => (
                <div key={index} className={`result-card ${result.isConsistent ? 'consistent' : 'inconsistent'}`}>
                  <div className="result-header">
                    <strong>{result.speaker}</strong>
                    <span className={`status-badge ${result.isConsistent ? 'good' : 'bad'}`}>
                      {result.isConsistent ? '✓ Consistent' : '⚠ Inconsistent'}
                    </span>
                  </div>

                  <div className="dialogue-text">"{result.dialogue}"</div>

                  <div className="voice-metrics">
                    <div className="metric">
                      <span>Formality:</span> {result.voiceProfile.formality}/100
                    </div>
                    <div className="metric">
                      <span>Complexity:</span> {result.voiceProfile.complexity}/100
                    </div>
                    <div className="metric">
                      <span>Tone:</span> {result.voiceProfile.tone}
                    </div>
                    <div className="metric">
                      <span>Style:</span> {result.voiceProfile.sentenceStyle}
                    </div>
                  </div>

                  {result.issues.length > 0 && (
                    <div className="issues">
                      <h4>Issues Found:</h4>
                      {result.issues.map((issue, i) => (
                        <div key={i} className={`issue severity-${issue.severity}`}>
                          <div className="issue-type">{issue.type}</div>
                          <div className="issue-desc">{issue.description}</div>
                          <div className="issue-suggestion">💡 {issue.suggestion}</div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Feature 2: Author Feedback */}
      {activeFeature === 'author' && (
        <div className="feature-section">
          <div className="section-header">
            <h2>Classic Author Feedback</h2>
            <p>Compare your writing to literary masters</p>
          </div>

          <div className="author-select">
            <label>Select Author:</label>
            <select value={selectedAuthor} onChange={(e) => setSelectedAuthor(e.target.value)}>
              {CLASSIC_AUTHORS.map(author => (
                <option key={author} value={author}>{author}</option>
              ))}
            </select>
            <button onClick={() => setAuthorText(SAMPLE_TEXT_FOR_AUTHOR)} className="btn-sample">
              Load Sample
            </button>
          </div>

          <textarea
            value={authorText}
            onChange={(e) => setAuthorText(e.target.value)}
            placeholder="Paste your writing here..."
            className="large-textarea"
            rows={8}
          />

          <button
            onClick={getAuthorFeedback}
            disabled={isLoading}
            className="btn-primary"
          >
            {isLoading ? 'Analyzing...' : `Compare to ${selectedAuthor}`}
          </button>

          {/* Author Feedback Results */}
          {authorFeedback && (
            <div className="results-section">
              <div className="score-card">
                <div className="score-circle">
                  <div className="score-value">{authorFeedback.matchScore}</div>
                  <div className="score-label">Match Score</div>
                </div>
                <p>How well your writing matches {authorFeedback.author}'s style</p>
              </div>

              <div className="feedback-grid">
                <div className="feedback-card strengths">
                  <h4>✓ Strengths</h4>
                  <ul>
                    {authorFeedback.strengths.map((s, i) => (
                      <li key={i}>{s}</li>
                    ))}
                  </ul>
                </div>

                <div className="feedback-card weaknesses">
                  <h4>✗ Weaknesses</h4>
                  <ul>
                    {authorFeedback.weaknesses.map((w, i) => (
                      <li key={i}>{w}</li>
                    ))}
                  </ul>
                </div>
              </div>

              <div className="suggestions-card">
                <h4>💡 Suggestions</h4>
                <ul>
                  {authorFeedback.suggestions.map((s, i) => (
                    <li key={i}>{s}</li>
                  ))}
                </ul>
              </div>

              {authorFeedback.rewrittenSample && (
                <div className="rewritten-card">
                  <h4>Rewritten in {authorFeedback.author}'s Style</h4>
                  <p className="rewritten-text">{authorFeedback.rewrittenSample}</p>
                </div>
              )}
            </div>
          )}
        </div>
      )}

      {/* Feature 3: Writing Categorization */}
      {activeFeature === 'categorize' && (
        <div className="feature-section">
          <div className="section-header">
            <h2>Writing Help Categorization</h2>
            <p>Identify what kind of help your writing needs</p>
          </div>

          <textarea
            value={categorizeText}
            onChange={(e) => setCategorizeText(e.target.value)}
            placeholder="Paste your writing here..."
            className="large-textarea"
            rows={8}
          />

          <button
            onClick={categorizeWriting}
            disabled={isLoading}
            className="btn-primary"
          >
            {isLoading ? 'Analyzing...' : 'Categorize Writing'}
          </button>

          {/* Category Results */}
          {category && (
            <div className="results-section">
              <div className="category-card">
                <div className="category-badge">{category.category}</div>
                <div className="confidence-bar">
                  <div className="confidence-fill" style={{ width: `${category.confidence}%` }} />
                </div>
                <div className="confidence-text">{category.confidence}% confident</div>
              </div>

              <div className="suggestions-card">
                <h4>Suggestions for {category.category}</h4>
                <ul>
                  {category.suggestions.map((s, i) => (
                    <li key={i}>{s}</li>
                  ))}
                </ul>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default CompetitionDemo;
