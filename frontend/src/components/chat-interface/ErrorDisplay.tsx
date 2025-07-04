import React from 'react';

interface ErrorDisplayProps {
  chatApiError?: string | null;
  apiGlobalError?: string | null;
  onTestConnection: () => Promise<void>;
}

/**
 * Molecular Component: Error Display
 * Single Responsibility: Display API errors and provide connection testing
 * Enhanced: Better error categorization and user guidance
 */
export const ErrorDisplay: React.FC<ErrorDisplayProps> = ({
  chatApiError,
  apiGlobalError,
  onTestConnection
}) => {
  const hasError = chatApiError || apiGlobalError;
  
  if (!hasError) return null;

  const errorMessage = chatApiError || apiGlobalError || '';
  
  // Categorize the error type for better user guidance
  const isAuthError = errorMessage.includes('Authentication') || 
                      errorMessage.includes('401') || 
                      errorMessage.includes('sign in') ||
                      errorMessage.includes('🔐');
  
  const isNetworkError = errorMessage.includes('Network') || 
                        errorMessage.includes('connection') ||
                        errorMessage.includes('🌐') ||
                        errorMessage.includes('🔌');
  
  const isTimeoutError = errorMessage.includes('timeout') || 
                        errorMessage.includes('⏱️');
  
  const isServerError = errorMessage.includes('Server') || 
                       errorMessage.includes('500') ||
                       errorMessage.includes('🔧');

  // Get appropriate icon and styling based on error type
  const getErrorIcon = () => {
    if (isAuthError) return '🔐';
    if (isNetworkError) return '🌐';
    if (isTimeoutError) return '⏱️';
    if (isServerError) return '🔧';
    return '⚠️';
  };

  const getErrorTitle = () => {
    if (isAuthError) return 'Authentication Required';
    if (isNetworkError) return 'Connection Issue';
    if (isTimeoutError) return 'Request Timeout';
    if (isServerError) return 'Server Error';
    return 'Error';
  };

  const getHelpText = () => {
    if (isAuthError) {
      return 'Please sign in again to continue using the AI Writing Assistant.';
    }
    if (isNetworkError) {
      return 'Check your internet connection and try again.';
    }
    if (isTimeoutError) {
      return 'The request took too long. Try with a shorter message.';
    }
    if (isServerError) {
      return 'The server is experiencing issues. Please try again in a moment.';
    }
    return 'Please try again or contact support if the problem persists.';
  };

  return (
    <div className={`chat-error-box ${isAuthError ? 'auth-error' : ''}`}>
      <div className="error-icon">{getErrorIcon()}</div>
      <div className="error-content">
        <div className="error-title">{getErrorTitle()}</div>
        <div className="error-message">
          {errorMessage}
        </div>
        <div className="error-help">
          {getHelpText()}
        </div>
        
        {/* Show different actions based on error type */}
        {isAuthError ? (
          <div className="error-actions">
            <button 
              className="auth-action-button"
              onClick={() => window.location.reload()}
            >
              🔄 Refresh Page
            </button>
          </div>
        ) : (
          <div className="error-actions">
            <button 
              className="test-connection-button"
              onClick={onTestConnection}
            >
              🔄 Test Connection
            </button>
          </div>
        )}
        
        {/* Debug info for developers */}
        {process.env.NODE_ENV === 'development' && (
          <details className="error-debug">
            <summary>🔍 Debug Information</summary>
            <pre className="debug-info">
              {JSON.stringify({
                chatApiError,
                apiGlobalError,
                errorType: {
                  isAuthError,
                  isNetworkError,
                  isTimeoutError,
                  isServerError
                },
                timestamp: new Date().toISOString(),
                userAgent: navigator.userAgent,
                url: window.location.href
              }, null, 2)}
            </pre>
          </details>
        )}
      </div>
    </div>
  );
}; 
 