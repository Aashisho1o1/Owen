import React from 'react';

interface ErrorDisplayProps {
  chatApiError?: string | null;
  apiGlobalError?: string | null;
  onTestConnection: () => Promise<void>;
}

/**
 * Molecular Component: Error Display
 * Single Responsibility: Display API errors and provide connection testing
 */
export const ErrorDisplay: React.FC<ErrorDisplayProps> = ({
  chatApiError,
  apiGlobalError,
  onTestConnection
}) => {
  const hasError = chatApiError || apiGlobalError;
  
  if (!hasError) return null;

  return (
    <div className="chat-error-box">
      <div className="error-icon">⚠️</div>
      <div className="error-content">
        <div className="error-title">Connection Issue</div>
        <div className="error-message">
          {chatApiError || apiGlobalError}
        </div>
        <button 
          className="test-connection-button"
          onClick={onTestConnection}
        >
          🔄 Test Connection
        </button>
      </div>
    </div>
  );
}; 
 