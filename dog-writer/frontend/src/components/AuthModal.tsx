import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';

interface AuthModalProps {
  isOpen: boolean;
  onClose: () => void;
  initialMode?: 'login' | 'register';
}

interface FormErrors {
  username?: string;
  email?: string;
  password?: string;
  display_name?: string;
  general?: string;
}

const AuthModal: React.FC<AuthModalProps> = ({ isOpen, onClose, initialMode = 'login' }) => {
  const { login, register, isLoading, error, clearError } = useAuth();
  const [mode, setMode] = useState<'login' | 'register'>(initialMode);
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: '',
    display_name: '',
    remember_me: false,
  });
  const [formErrors, setFormErrors] = useState<FormErrors>({});
  const [showPassword, setShowPassword] = useState(false);

  // Clear form and errors when modal opens/closes
  useEffect(() => {
    if (isOpen) {
      setFormData({
        username: '',
        email: '',
        password: '',
        display_name: '',
        remember_me: false,
      });
      setFormErrors({});
      clearError();
    }
  }, [isOpen, clearError]);

  // Clear errors when switching modes
  useEffect(() => {
    setFormErrors({});
    clearError();
  }, [mode, clearError]);

  const validateForm = (): boolean => {
    const errors: FormErrors = {};

    // Username validation
    if (!formData.username.trim()) {
      errors.username = 'Username is required';
    } else if (formData.username.length < 3) {
      errors.username = 'Username must be at least 3 characters';
    } else if (!/^[a-zA-Z0-9_]+$/.test(formData.username)) {
      errors.username = 'Username can only contain letters, numbers, and underscores';
    }

    // Email validation (only for registration)
    if (mode === 'register') {
      if (!formData.email.trim()) {
        errors.email = 'Email is required';
      } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {
        errors.email = 'Please enter a valid email address';
      }
    }

    // Password validation
    if (!formData.password) {
      errors.password = 'Password is required';
    } else if (mode === 'register' && formData.password.length < 8) {
      errors.password = 'Password must be at least 8 characters';
    } else if (mode === 'register' && !/(?=.*[a-zA-Z])(?=.*\d)(?=.*[!@#$%^&*(),.?":{}|<>])/.test(formData.password)) {
      errors.password = 'Password must contain letters, numbers, and special characters';
    } else if (mode === 'register') {
      // Check for common weak passwords
      const weakPasswords = [
        'password', 'password123', '12345678', 'qwerty123', 'abc123456',
        'password1', 'welcome123', 'admin123', 'user1234', 'letmein123'
      ];
      if (weakPasswords.includes(formData.password.toLowerCase())) {
        errors.password = 'Password is too common. Please choose a stronger password';
      }
    }

    setFormErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!validateForm()) {
      return;
    }

    let success = false;

    if (mode === 'login') {
      success = await login({
        username: formData.username,
        password: formData.password,
        remember_me: formData.remember_me,
      });
    } else {
      success = await register({
        username: formData.username,
        email: formData.email,
        password: formData.password,
        display_name: formData.display_name || undefined,
      });
    }

    if (success) {
      onClose();
    }
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value, type, checked } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value,
    }));
    
    // Clear field-specific errors when user starts typing
    if (formErrors[name as keyof FormErrors]) {
      setFormErrors(prev => ({
        ...prev,
        [name]: undefined,
      }));
    }
  };

  const switchMode = () => {
    setMode(mode === 'login' ? 'register' : 'login');
  };

  if (!isOpen) return null;

  return (
    <div className="auth-modal-overlay" onClick={onClose}>
      <div className="auth-modal" onClick={(e) => e.stopPropagation()}>
        <div className="auth-modal-header">
          <h2>{mode === 'login' ? 'Welcome Back' : 'Create Your Account'}</h2>
          <button className="auth-modal-close" onClick={onClose} aria-label="Close">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <line x1="18" y1="6" x2="6" y2="18"></line>
              <line x1="6" y1="6" x2="18" y2="18"></line>
            </svg>
          </button>
        </div>

        <div className="auth-modal-content">
          <form onSubmit={handleSubmit} className="auth-form">
            {/* General error display */}
            {error && (
              <div className="auth-error-banner">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <circle cx="12" cy="12" r="10"></circle>
                  <line x1="15" y1="9" x2="9" y2="15"></line>
                  <line x1="9" y1="9" x2="15" y2="15"></line>
                </svg>
                {error}
              </div>
            )}

            {/* Username field */}
            <div className="auth-form-group">
              <label htmlFor="username" className="auth-form-label">
                Username {mode === 'login' && '/ Email'}
              </label>
              <input
                type="text"
                id="username"
                name="username"
                value={formData.username}
                onChange={handleInputChange}
                className={`auth-form-input ${formErrors.username ? 'error' : ''}`}
                placeholder={mode === 'login' ? 'Enter username or email' : 'Choose a username'}
                disabled={isLoading}
                autoComplete="username"
              />
              {formErrors.username && (
                <span className="auth-form-error">{formErrors.username}</span>
              )}
            </div>

            {/* Email field (registration only) */}
            {mode === 'register' && (
              <div className="auth-form-group">
                <label htmlFor="email" className="auth-form-label">
                  Email Address
                </label>
                <input
                  type="email"
                  id="email"
                  name="email"
                  value={formData.email}
                  onChange={handleInputChange}
                  className={`auth-form-input ${formErrors.email ? 'error' : ''}`}
                  placeholder="your.email@example.com"
                  disabled={isLoading}
                  autoComplete="email"
                />
                {formErrors.email && (
                  <span className="auth-form-error">{formErrors.email}</span>
                )}
              </div>
            )}

            {/* Display name field (registration only, optional) */}
            {mode === 'register' && (
              <div className="auth-form-group">
                <label htmlFor="display_name" className="auth-form-label">
                  Display Name <span className="auth-form-optional">(optional)</span>
                </label>
                <input
                  type="text"
                  id="display_name"
                  name="display_name"
                  value={formData.display_name}
                  onChange={handleInputChange}
                  className="auth-form-input"
                  placeholder="How should we call you?"
                  disabled={isLoading}
                  autoComplete="name"
                />
              </div>
            )}

            {/* Password field */}
            <div className="auth-form-group">
              <label htmlFor="password" className="auth-form-label">
                Password
              </label>
              <div className="auth-password-container">
                <input
                  type={showPassword ? 'text' : 'password'}
                  id="password"
                  name="password"
                  value={formData.password}
                  onChange={handleInputChange}
                  className={`auth-form-input ${formErrors.password ? 'error' : ''}`}
                  placeholder={mode === 'register' ? 'Create a strong password' : 'Enter your password'}
                  disabled={isLoading}
                  autoComplete={mode === 'register' ? 'new-password' : 'current-password'}
                />
                <button
                  type="button"
                  className="auth-password-toggle"
                  onClick={() => setShowPassword(!showPassword)}
                  disabled={isLoading}
                  aria-label={showPassword ? 'Hide password' : 'Show password'}
                >
                  {showPassword ? (
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                      <path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"></path>
                      <line x1="1" y1="1" x2="23" y2="23"></line>
                    </svg>
                  ) : (
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                      <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path>
                      <circle cx="12" cy="12" r="3"></circle>
                    </svg>
                  )}
                </button>
              </div>
              {formErrors.password && (
                <span className="auth-form-error">{formErrors.password}</span>
              )}
              {mode === 'register' && (
                <div className="auth-password-requirements">
                  <small>Password must be at least 8 characters with letters, numbers, and special characters</small>
                </div>
              )}
            </div>

            {/* Remember me checkbox (login only) */}
            {mode === 'login' && (
              <div className="auth-form-group-checkbox">
                <label className="auth-checkbox-label">
                  <input
                    type="checkbox"
                    name="remember_me"
                    checked={formData.remember_me}
                    onChange={handleInputChange}
                    disabled={isLoading}
                  />
                  <span className="auth-checkbox-custom"></span>
                  Keep me signed in for 30 days
                </label>
              </div>
            )}

            {/* Submit button */}
            <button
              type="submit"
              className="auth-form-submit"
              disabled={isLoading}
            >
              {isLoading ? (
                <div className="auth-loading-spinner">
                  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                    <path d="M21 12a9 9 0 11-6.219-8.56" />
                  </svg>
                </div>
              ) : (
                mode === 'login' ? 'Sign In' : 'Create Account'
              )}
            </button>
          </form>

          {/* Mode switch */}
          <div className="auth-mode-switch">
            {mode === 'login' ? (
              <p>
                Don't have an account?{' '}
                <button
                  type="button"
                  className="auth-link-button"
                  onClick={switchMode}
                  disabled={isLoading}
                >
                  Create one here
                </button>
              </p>
            ) : (
              <p>
                Already have an account?{' '}
                <button
                  type="button"
                  className="auth-link-button"
                  onClick={switchMode}
                  disabled={isLoading}
                >
                  Sign in instead
                </button>
              </p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default AuthModal; 