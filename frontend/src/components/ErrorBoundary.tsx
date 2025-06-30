import React, { Component, ErrorInfo, ReactNode } from 'react';
import { logger } from '../utils/logger';

interface Props {
  children: ReactNode;
  fallback?: ReactNode;
  onError?: (error: Error, errorInfo: ErrorInfo) => void;
}

interface State {
  hasError: boolean;
  error?: Error;
}

/**
 * Error Boundary Component
 * Catches JavaScript errors anywhere in the child component tree,
 * logs those errors, and displays a fallback UI instead of crashing the app.
 * 
 * CRITICAL: Addresses security issue identified by Claude Opus
 */
export class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError(error: Error): State {
    // Update state so the next render will show the fallback UI
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    // SECURITY: Log error details for monitoring
    logger.error('🚨 ERROR BOUNDARY: Component error caught', {
      error: error.message,
      stack: error.stack,
      componentStack: errorInfo.componentStack,
      timestamp: new Date().toISOString()
    });

    // Call custom error handler if provided
    if (this.props.onError) {
      this.props.onError(error, errorInfo);
    }

    // In production, you might want to send this to an error reporting service
    if (process.env.NODE_ENV === 'production') {
      // TODO: Send to error monitoring service (e.g., Sentry)
      console.error('Production error caught by boundary:', error);
    }
  }

  render() {
    if (this.state.hasError) {
      // Custom fallback UI
      if (this.props.fallback) {
        return this.props.fallback;
      }

      // Default fallback UI
      return (
        <div className="error-boundary">
          <div className="error-boundary-content">
            <h2>🚨 Something went wrong</h2>
            <p>
              We're sorry, but something unexpected happened. The application has 
              been protected from crashing, but this component couldn't load properly.
            </p>
            <details className="error-details">
              <summary>Error Details (for developers)</summary>
              <pre>{this.state.error?.message}</pre>
              {process.env.NODE_ENV === 'development' && (
                <pre>{this.state.error?.stack}</pre>
              )}
            </details>
            <button 
              onClick={() => this.setState({ hasError: false, error: undefined })}
              className="error-retry-button"
            >
              Try Again
            </button>
            <button 
              onClick={() => window.location.reload()}
              className="error-reload-button"
            >
              Reload Page
            </button>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
} 