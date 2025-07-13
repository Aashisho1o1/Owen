import React, { useState } from 'react';
import { ModalContainer } from './auth/ModalContainer';

interface StoryGeneratorModalProps {
  isOpen: boolean;
  onClose: () => void;
}

// Story generator options - carefully curated for viral potential
const STORY_SPARKS = [
  "✨ Custom idea",
  "☕ A barista discovers their coffee shop exists in multiple dimensions",
  "🚚 Two rival food truck owners get snowed in together overnight", 
  "📚 A librarian finds books that write themselves based on patron's secrets",
  "🎭 An actor realizes they're living in someone else's dream",
  "🌧️ Every time it rains, the same stranger appears at your door",
  "📱 Your phone starts receiving texts from your future self",
  "🗝️ A locksmith discovers keys that unlock memories instead of doors",
  "🎨 A street artist's paintings start coming to life at midnight",
  "🚂 The last train of the night only appears to people who need to escape"
];

const READER_EMOTIONS = [
  "Wonder and amazement",
  "Warm nostalgia", 
  "Gentle melancholy",
  "Quiet hope",
  "Peaceful contentment",
  "Bittersweet joy",
  "Thrilling excitement",
  "Cozy comfort",
  "Mysterious intrigue",
  "Heartwarming connection"
];

// Reuse existing author personas from ChatHeader for consistency
const AUTHOR_VIBES = [
  "Ernest Hemingway",
  "Virginia Woolf",
  "Maya Angelou", 
  "Haruki Murakami",
  "Toni Morrison",
  "Neil Gaiman",
  "George Orwell",
  "J.K. Rowling",
  "Margaret Atwood"
];

const STORY_LENGTHS = [
  "Short (300-500 words)",
  "Medium (500-800 words)", 
  "Long (800-1200 words)"
];

interface StoryGenerateRequest {
  story_spark: string;
  reader_emotion: string;
  author_vibe: string;
  story_length: string;
}

interface StoryGenerateResponse {
  story: string;
  inputs: StoryGenerateRequest;
  success: boolean;
}

export const StoryGeneratorModal: React.FC<StoryGeneratorModalProps> = ({
  isOpen,
  onClose
}) => {
  // Form state - following React best practices
  const [storySpark, setStorySpark] = useState(STORY_SPARKS[1]); // Start with first actual story, not custom
  const [customSpark, setCustomSpark] = useState('');
  const [readerEmotion, setReaderEmotion] = useState(READER_EMOTIONS[0]);
  const [authorVibe, setAuthorVibe] = useState(AUTHOR_VIBES[0]);
  const [storyLength, setStoryLength] = useState(STORY_LENGTHS[0]);
  
  // UI state
  const [isGenerating, setIsGenerating] = useState(false);
  const [generatedStory, setGeneratedStory] = useState('');
  const [error, setError] = useState('');
  const [copyStatus, setCopyStatus] = useState<'idle' | 'copying' | 'success' | 'error'>('idle');

  // Reset form when modal closes
  React.useEffect(() => {
    if (!isOpen) {
      setGeneratedStory('');
      setError('');
      setCopyStatus('idle');
    }
  }, [isOpen]);

  const handleGenerate = async () => {
    try {
      setIsGenerating(true);
      setError('');
      
      // Determine final story spark (custom or selected)
      const finalSpark = storySpark === "✨ Custom idea" ? customSpark.trim() : storySpark;
      
      // Validate custom input
      if (storySpark === "✨ Custom idea" && !finalSpark) {
        setError('Please enter your custom story idea.');
        return;
      }
      
      // Get auth token - following existing auth patterns
      const token = localStorage.getItem('access_token');
      if (!token) {
        setError('Please sign in to generate stories.');
        return;
      }
      
      // Make API request to our new endpoint
      const response = await fetch('/api/story-generator/generate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          story_spark: finalSpark,
          reader_emotion: readerEmotion,
          author_vibe: authorVibe,
          story_length: storyLength
        })
      });
      
      if (!response.ok) {
        if (response.status === 401) {
          throw new Error('Please sign in to generate stories.');
        } else if (response.status === 429) {
          throw new Error('Too many requests. Please wait a moment and try again.');
        } else {
          throw new Error('Failed to generate story. Please try again.');
        }
      }
      
      const data: StoryGenerateResponse = await response.json();
      setGeneratedStory(data.story);
      
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to generate story. Please try again.';
      setError(errorMessage);
    } finally {
      setIsGenerating(false);
    }
  };

  const handleCopyStory = async () => {
    try {
      setCopyStatus('copying');
      
      // Use the same clipboard logic as WritingWorkspace
      if (navigator.clipboard && window.isSecureContext) {
        await navigator.clipboard.writeText(generatedStory);
      } else {
        // Fallback for older browsers
        const textArea = document.createElement('textarea');
        textArea.value = generatedStory;
        textArea.style.position = 'fixed';
        textArea.style.left = '-999999px';
        textArea.style.top = '-999999px';
        document.body.appendChild(textArea);
        textArea.focus();
        textArea.select();
        document.execCommand('copy');
        textArea.remove();
      }
      
      setCopyStatus('success');
      setTimeout(() => setCopyStatus('idle'), 2000);
    } catch (err) {
      console.error('Failed to copy story:', err);
      setCopyStatus('error');
      setTimeout(() => setCopyStatus('idle'), 2000);
    }
  };

  const handleGenerateAnother = () => {
    setGeneratedStory('');
    setError('');
    setCopyStatus('idle');
  };

  // Render form inputs - reusing existing styling patterns
  const renderForm = () => (
    <div style={{ maxWidth: '600px', padding: '20px' }}>
      {/* Story Idea Selection */}
      <div style={{ marginBottom: '20px' }}>
        <label style={{ 
          display: 'block', 
          marginBottom: '8px', 
          fontWeight: '600',
          color: 'var(--text-primary)',
          fontSize: '14px'
        }}>
          📝 Story Idea
        </label>
        <select 
          value={storySpark}
          onChange={(e) => setStorySpark(e.target.value)}
          style={{ 
            width: '100%', 
            padding: '12px', 
            borderRadius: '8px', 
            border: '2px solid var(--border-color)',
            background: 'var(--bg-primary)',
            color: 'var(--text-primary)',
            fontSize: '14px',
            transition: 'border-color 0.2s'
          }}
          onFocus={(e) => e.target.style.borderColor = 'var(--accent-color)'}
          onBlur={(e) => e.target.style.borderColor = 'var(--border-color)'}
        >
          {STORY_SPARKS.map(spark => (
            <option key={spark} value={spark}>{spark}</option>
          ))}
        </select>
        
        {/* Custom idea input */}
        {storySpark === "✨ Custom idea" && (
          <input
            type="text"
            value={customSpark}
            onChange={(e) => setCustomSpark(e.target.value)}
            placeholder="Enter your story idea... (e.g., 'A chef who can taste emotions in food')"
            style={{ 
              width: '100%', 
              padding: '12px', 
              marginTop: '12px', 
              borderRadius: '8px', 
              border: '2px solid var(--border-color)',
              background: 'var(--bg-primary)',
              color: 'var(--text-primary)',
              fontSize: '14px',
              transition: 'border-color 0.2s'
            }}
            onFocus={(e) => e.target.style.borderColor = 'var(--accent-color)'}
            onBlur={(e) => e.target.style.borderColor = 'var(--border-color)'}
          />
        )}
      </div>

      {/* Reader Emotion Selection */}
      <div style={{ marginBottom: '20px' }}>
        <label style={{ 
          display: 'block', 
          marginBottom: '8px', 
          fontWeight: '600',
          color: 'var(--text-primary)',
          fontSize: '14px'
        }}>
          💝 Desired Reader Emotion
        </label>
        <select 
          value={readerEmotion}
          onChange={(e) => setReaderEmotion(e.target.value)}
          style={{ 
            width: '100%', 
            padding: '12px', 
            borderRadius: '8px', 
            border: '2px solid var(--border-color)',
            background: 'var(--bg-primary)',
            color: 'var(--text-primary)',
            fontSize: '14px',
            transition: 'border-color 0.2s'
          }}
          onFocus={(e) => e.target.style.borderColor = 'var(--accent-color)'}
          onBlur={(e) => e.target.style.borderColor = 'var(--border-color)'}
        >
          {READER_EMOTIONS.map(emotion => (
            <option key={emotion} value={emotion}>{emotion}</option>
          ))}
        </select>
      </div>

      {/* Author Style Selection */}
      <div style={{ marginBottom: '20px' }}>
        <label style={{ 
          display: 'block', 
          marginBottom: '8px', 
          fontWeight: '600',
          color: 'var(--text-primary)',
          fontSize: '14px'
        }}>
          ✍️ Author Style Inspiration
        </label>
        <select 
          value={authorVibe}
          onChange={(e) => setAuthorVibe(e.target.value)}
          style={{ 
            width: '100%', 
            padding: '12px', 
            borderRadius: '8px', 
            border: '2px solid var(--border-color)',
            background: 'var(--bg-primary)',
            color: 'var(--text-primary)',
            fontSize: '14px',
            transition: 'border-color 0.2s'
          }}
          onFocus={(e) => e.target.style.borderColor = 'var(--accent-color)'}
          onBlur={(e) => e.target.style.borderColor = 'var(--border-color)'}
        >
          {AUTHOR_VIBES.map(vibe => (
            <option key={vibe} value={vibe}>{vibe}</option>
          ))}
        </select>
      </div>

      {/* Story Length Selection */}
      <div style={{ marginBottom: '24px' }}>
        <label style={{ 
          display: 'block', 
          marginBottom: '8px', 
          fontWeight: '600',
          color: 'var(--text-primary)',
          fontSize: '14px'
        }}>
          📏 Story Length
        </label>
        <select 
          value={storyLength}
          onChange={(e) => setStoryLength(e.target.value)}
          style={{ 
            width: '100%', 
            padding: '12px', 
            borderRadius: '8px', 
            border: '2px solid var(--border-color)',
            background: 'var(--bg-primary)',
            color: 'var(--text-primary)',
            fontSize: '14px',
            transition: 'border-color 0.2s'
          }}
          onFocus={(e) => e.target.style.borderColor = 'var(--accent-color)'}
          onBlur={(e) => e.target.style.borderColor = 'var(--border-color)'}
        >
          {STORY_LENGTHS.map(length => (
            <option key={length} value={length}>{length}</option>
          ))}
        </select>
      </div>

      {/* Error Display */}
      {error && (
        <div style={{ 
          color: '#ef4444', 
          marginBottom: '20px', 
          padding: '12px', 
          background: '#fee2e2', 
          borderRadius: '8px',
          border: '1px solid #fecaca',
          fontSize: '14px'
        }}>
          ⚠️ {error}
        </div>
      )}

      {/* Action Buttons */}
      <div style={{ display: 'flex', gap: '12px', justifyContent: 'flex-end' }}>
        <button
          onClick={onClose}
          style={{ 
            padding: '12px 24px', 
            border: '2px solid var(--border-color)', 
            background: 'var(--bg-primary)', 
            color: 'var(--text-primary)',
            borderRadius: '8px', 
            cursor: 'pointer',
            fontSize: '14px',
            fontWeight: '500',
            transition: 'all 0.2s'
          }}
          onMouseEnter={(e) => {
            e.currentTarget.style.background = 'var(--bg-secondary)';
            e.currentTarget.style.borderColor = 'var(--accent-color)';
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.background = 'var(--bg-primary)';
            e.currentTarget.style.borderColor = 'var(--border-color)';
          }}
        >
          Cancel
        </button>
        <button
          onClick={handleGenerate}
          disabled={isGenerating || (storySpark === "✨ Custom idea" && !customSpark.trim())}
          style={{ 
            padding: '12px 24px', 
            background: isGenerating ? '#9ca3af' : '#3b82f6', 
            color: 'white', 
            border: 'none', 
            borderRadius: '8px', 
            cursor: isGenerating ? 'not-allowed' : 'pointer',
            fontSize: '14px',
            fontWeight: '600',
            transition: 'background-color 0.2s',
            opacity: (isGenerating || (storySpark === "✨ Custom idea" && !customSpark.trim())) ? 0.7 : 1
          }}
          onMouseEnter={(e) => {
            if (!isGenerating && !(storySpark === "✨ Custom idea" && !customSpark.trim())) {
              e.currentTarget.style.background = '#2563eb';
            }
          }}
          onMouseLeave={(e) => {
            if (!isGenerating) {
              e.currentTarget.style.background = '#3b82f6';
            }
          }}
        >
          {isGenerating ? '✨ Generating...' : '✨ Generate Story'}
        </button>
      </div>
    </div>
  );

  // Render generated story display
  const renderStory = () => (
    <div style={{ maxWidth: '700px', padding: '20px' }}>
      {/* Story Display */}
      <div style={{ 
        marginBottom: '20px', 
        maxHeight: '400px', 
        overflow: 'auto', 
        padding: '20px', 
        background: 'var(--bg-secondary)', 
        borderRadius: '12px', 
        border: '1px solid var(--border-color)',
        fontFamily: 'Georgia, serif',
        lineHeight: '1.6',
        fontSize: '15px'
      }}>
        <pre style={{ 
          whiteSpace: 'pre-wrap', 
          fontFamily: 'inherit', 
          margin: 0,
          color: 'var(--text-primary)'
        }}>
          {generatedStory}
        </pre>
      </div>
      
      {/* Action Buttons */}
      <div style={{ display: 'flex', gap: '12px', justifyContent: 'flex-end', flexWrap: 'wrap' }}>
        <button
          onClick={handleGenerateAnother}
          style={{ 
            padding: '12px 20px', 
            border: '2px solid var(--border-color)', 
            background: 'var(--bg-primary)', 
            color: 'var(--text-primary)',
            borderRadius: '8px', 
            cursor: 'pointer',
            fontSize: '14px',
            fontWeight: '500',
            transition: 'all 0.2s'
          }}
          onMouseEnter={(e) => {
            e.currentTarget.style.background = 'var(--bg-secondary)';
            e.currentTarget.style.borderColor = 'var(--accent-color)';
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.background = 'var(--bg-primary)';
            e.currentTarget.style.borderColor = 'var(--border-color)';
          }}
        >
          🔄 Generate Another
        </button>
        
        <button
          onClick={handleCopyStory}
          disabled={copyStatus === 'copying'}
          style={{ 
            padding: '12px 20px', 
            background: copyStatus === 'success' ? '#10b981' : 
                       copyStatus === 'error' ? '#ef4444' : '#059669',
            color: 'white', 
            border: 'none', 
            borderRadius: '8px', 
            cursor: copyStatus === 'copying' ? 'not-allowed' : 'pointer',
            fontSize: '14px',
            fontWeight: '600',
            transition: 'background-color 0.2s',
            opacity: copyStatus === 'copying' ? 0.7 : 1
          }}
        >
          {copyStatus === 'copying' && '⏳ Copying...'}
          {copyStatus === 'success' && '✅ Copied!'}
          {copyStatus === 'error' && '❌ Failed'}
          {copyStatus === 'idle' && '📋 Copy Story'}
        </button>
        
        <button
          onClick={onClose}
          style={{ 
            padding: '12px 20px', 
            background: '#3b82f6', 
            color: 'white', 
            border: 'none', 
            borderRadius: '8px', 
            cursor: 'pointer',
            fontSize: '14px',
            fontWeight: '600',
            transition: 'background-color 0.2s'
          }}
          onMouseEnter={(e) => e.currentTarget.style.background = '#2563eb'}
          onMouseLeave={(e) => e.currentTarget.style.background = '#3b82f6'}
        >
          Done
        </button>
      </div>
    </div>
  );

  return (
    <ModalContainer
      isOpen={isOpen}
      onClose={onClose}
      title="🎨 AI Story Generator"
    >
      {!generatedStory ? renderForm() : renderStory()}
    </ModalContainer>
  );
}; 