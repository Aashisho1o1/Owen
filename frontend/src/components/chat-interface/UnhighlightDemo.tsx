import React, { useState } from 'react';
import { UnhighlightButton } from './UnhighlightButton';

/**
 * Demo Component: Unhighlight Feature Demonstration
 * Shows how the new unhighlight system works
 */
export const UnhighlightDemo: React.FC = () => {
  const [demoHighlightedText, setDemoHighlightedText] = useState<string>('');

  const handleDemoHighlight = (text: string) => {
    setDemoHighlightedText(text);
  };

  const clearDemoHighlight = () => {
    setDemoHighlightedText('');
  };

  return (
    <div style={{ 
      padding: '20px', 
      border: '2px solid #e5e7eb', 
      borderRadius: '8px',
      margin: '20px',
      fontFamily: 'Inter, sans-serif'
    }}>
      <h3>🎯 Unhighlight Feature Demo</h3>
      
      <div style={{ marginBottom: '16px' }}>
        <h4>✨ Key Features:</h4>
        <ul>
          <li>✅ <strong>Auto-clear previous highlights</strong> when selecting new text</li>
          <li>✅ <strong>Manual unhighlight button</strong> (🧹 Unhighlight)</li>
          <li>✅ <strong>Clean, uncluttered experience</strong></li>
        </ul>
      </div>

      <div style={{ marginBottom: '16px' }}>
        <h4>📝 Sample Text (click to highlight):</h4>
        <div style={{ 
          padding: '12px', 
          backgroundColor: '#f8f9fa', 
          borderRadius: '6px',
          lineHeight: '1.6'
        }}>
          <span 
            onClick={() => handleDemoHighlight('The sun was setting')}
            style={{ 
              cursor: 'pointer',
              backgroundColor: demoHighlightedText === 'The sun was setting' ? '#fef3c7' : 'transparent',
              padding: '2px 4px',
              borderRadius: '3px',
              fontWeight: demoHighlightedText === 'The sun was setting' ? 'bold' : 'normal'
            }}
          >
            The sun was setting
          </span>
          {' '}over the horizon, casting long shadows across the{' '}
          <span 
            onClick={() => handleDemoHighlight('peaceful meadow')}
            style={{ 
              cursor: 'pointer',
              backgroundColor: demoHighlightedText === 'peaceful meadow' ? '#fef3c7' : 'transparent',
              padding: '2px 4px',
              borderRadius: '3px',
              fontWeight: demoHighlightedText === 'peaceful meadow' ? 'bold' : 'normal'
            }}
          >
            peaceful meadow
          </span>
          . The birds were singing their{' '}
          <span 
            onClick={() => handleDemoHighlight('evening songs')}
            style={{ 
              cursor: 'pointer',
              backgroundColor: demoHighlightedText === 'evening songs' ? '#fef3c7' : 'transparent',
              padding: '2px 4px',
              borderRadius: '3px',
              fontWeight: demoHighlightedText === 'evening songs' ? 'bold' : 'normal'
            }}
          >
            evening songs
          </span>
          , creating a symphony of nature.
        </div>
      </div>

      <div style={{ marginBottom: '16px' }}>
        <h4>🎮 Try it out:</h4>
        <ol>
          <li>Click on any highlighted phrase above</li>
          <li>Notice how previous highlights automatically clear</li>
          <li>Use the unhighlight button to clear all highlights</li>
        </ol>
      </div>

      <div style={{ 
        display: 'flex', 
        alignItems: 'center', 
        gap: '12px',
        padding: '12px',
        backgroundColor: '#f3f4f6',
        borderRadius: '6px'
      }}>
        <span>Currently highlighted:</span>
        <strong style={{ color: '#059669' }}>
          {demoHighlightedText || 'None'}
        </strong>
        
        {demoHighlightedText && (
          <button
            onClick={clearDemoHighlight}
            style={{
              background: 'linear-gradient(135deg, #ef4444 0%, #dc2626 100%)',
              color: 'white',
              border: 'none',
              borderRadius: '6px',
              padding: '6px 10px',
              fontSize: '12px',
              fontWeight: '500',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '4px'
            }}
          >
            🧹 Unhighlight
          </button>
        )}
      </div>

      <div style={{ 
        marginTop: '16px',
        padding: '12px',
        backgroundColor: '#ecfdf5',
        borderRadius: '6px',
        border: '1px solid #10b981'
      }}>
        <h4 style={{ color: '#065f46', margin: '0 0 8px 0' }}>✅ Implementation Status:</h4>
        <ul style={{ margin: 0, color: '#047857' }}>
          <li>✅ Auto-clear previous highlights</li>
          <li>✅ UnhighlightButton component created</li>
          <li>✅ ChatContext enhanced with clearAllTextHighlights()</li>
          <li>✅ Editor components support clear-all action</li>
          <li>✅ Beautiful styling with hover effects</li>
          <li>✅ Integrated into ChatHeader and MessagesContainer</li>
        </ul>
      </div>
    </div>
  );
}; 