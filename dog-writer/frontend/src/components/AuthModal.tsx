import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import '../styles/auth.css';

interface AuthModalProps {
  isOpen: boolean;
  onClose: () => void;
  initialMode?: 'signin' | 'signup';
}

interface FormData {
  name: string;
  email: string;
  password: string;
  confirmPassword: string;
  agreeToTerms: boolean;
}

interface FormErrors {
  name?: string;
  email?: string;
  password?: string;
  confirmPassword?: string;
  agreeToTerms?: string;
  submit?: string;
}

const AuthModal: React.FC<AuthModalProps> = ({ isOpen, onClose, initialMode = 'signin' }) => {
  const { login, register, isLoading, error: authError } = useAuth();
  const [mode, setMode] = useState<'signin' | 'signup'>(initialMode);
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  
  const [formData, setFormData] = useState<FormData>({
    name: '',
    email: '',
    password: '',
    confirmPassword: '',
    agreeToTerms: false
  });
  
  const [errors, setErrors] = useState<FormErrors>({});
  const [isSubmitting, setIsSubmitting] = useState(false);

  // Reset form when mode changes
  useEffect(() => {
    setFormData({
      name: '',
      email: '',
      password: '',
      confirmPassword: '',
      agreeToTerms: false
    });
    setErrors({});
    setShowPassword(false);
    setShowConfirmPassword(false);
  }, [mode]);

  // Reset form when modal opens/closes
  useEffect(() => {
    if (!isOpen) {
      setFormData({
        name: '',
        email: '',
        password: '',
        confirmPassword: '',
        agreeToTerms: false
      });
      setErrors({});
      setShowPassword(false);
      setShowConfirmPassword(false);
    }
  }, [isOpen]);

  // Handle input changes
  const handleInputChange = (field: keyof FormData, value: string | boolean) => {
    setFormData(prev => ({ ...prev, [field]: value }));
    
    // Clear specific field error when user starts typing
    if (errors[field as keyof FormErrors]) {
      setErrors(prev => ({ ...prev, [field]: undefined }));
    }
  };

  // Validate form
  const validateForm = (): boolean => {
    const newErrors: FormErrors = {};
    
    // Email validation
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!formData.email.trim()) {
      newErrors.email = 'Email is required';
    } else if (!emailRegex.test(formData.email)) {
      newErrors.email = 'Please enter a valid email address';
    }

    // Password validation
    if (!formData.password) {
      newErrors.password = 'Password is required';
    } else if (formData.password.length < 8) {
      newErrors.password = 'Password must be at least 8 characters long';
    }

    if (mode === 'signup') {
      // Name validation for signup
      if (!formData.name.trim()) {
        newErrors.name = 'Name is required';
      } else if (formData.name.trim().length < 2) {
        newErrors.name = 'Name must be at least 2 characters long';
      }

      // Confirm password validation for signup
      if (!formData.confirmPassword) {
        newErrors.confirmPassword = 'Please confirm your password';
      } else if (formData.password !== formData.confirmPassword) {
        newErrors.confirmPassword = 'Passwords do not match';
      }

      // Terms agreement validation for signup
      if (!formData.agreeToTerms) {
        newErrors.agreeToTerms = 'Please agree to the terms and conditions';
      }
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  // Handle form submission
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!validateForm()) {
      return;
    }

    setIsSubmitting(true);
    
    try {
      if (mode === 'signin') {
        await login(formData.email, formData.password);
      } else {
        await register(formData.name, formData.email, formData.password);
      }
      
      // If successful, the AuthProvider will handle the user state and token
      // We can just close the modal.
      onClose();
    } catch (err) {
      // The error is already handled by the AuthContext, but we can set a local error if needed.
      // The authError from useAuth() will also be populated.
      setErrors({ submit: 'Authentication failed. Please check your credentials.' });
    } finally {
      setIsSubmitting(false);
    }
  };

  // Handle modal backdrop click
  const handleBackdropClick = (e: React.MouseEvent) => {
    if (e.target === e.currentTarget) {
      onClose();
    }
  };

  // Handle escape key
  useEffect(() => {
    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape' && isOpen) {
        onClose();
      }
    };

    if (isOpen) {
      document.addEventListener('keydown', handleEscape);
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = 'unset';
    }

    return () => {
      document.removeEventListener('keydown', handleEscape);
      document.body.style.overflow = 'unset';
    };
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  return (
    <div className="auth-modal-overlay" onClick={handleBackdropClick}>
      <div className="auth-modal" role="dialog" aria-labelledby="auth-modal-title" aria-modal="true">
        {/* Header */}
        <div className="auth-modal-header">
          <h2 id="auth-modal-title">
            {mode === 'signin' ? 'Welcome Back' : 'Create Account'}
          </h2>
          <button 
            className="auth-modal-close" 
            onClick={onClose}
            aria-label="Close authentication modal"
          >
            <svg width="20" height="20" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M15 5L5 15M5 5L15 15" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
            </svg>
          </button>
        </div>

        {/* Content */}
        <div className="auth-modal-content">
          {/* Error Banner */}
          {(authError || errors.submit) && (
            <div className="auth-error-banner">
              <svg width="16" height="16" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M8 15A7 7 0 1 1 8 1a7 7 0 0 1 0 14zM8 4v4M8 10h.01" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
              </svg>
              <span>{authError || errors.submit}</span>
            </div>
          )}

          {/* Form */}
          <form className="auth-form" onSubmit={handleSubmit} noValidate>
            {/* Name Field (Signup only) */}
            {mode === 'signup' && (
              <div className="auth-form-group">
                <label htmlFor="auth-name" className="auth-form-label">
                  Full Name
                </label>
                <input
                  id="auth-name"
                  type="text"
                  className={`auth-form-input ${errors.name ? 'error' : ''}`}
                  placeholder="Enter your full name"
                  value={formData.name}
                  onChange={(e) => handleInputChange('name', e.target.value)}
                  disabled={isSubmitting || isLoading}
                  autoComplete="name"
                />
                {errors.name && (
                  <div className="auth-form-error">
                    <svg width="12" height="12" viewBox="0 0 12 12" fill="none" xmlns="http://www.w3.org/2000/svg">
                      <path d="M6 11A5 5 0 1 1 6 1a5 5 0 0 1 0 10zM6 3v3M6 8h.01" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
                    </svg>
                    {errors.name}
                  </div>
                )}
              </div>
            )}

            {/* Email Field */}
            <div className="auth-form-group">
              <label htmlFor="auth-email" className="auth-form-label">
                Email Address
              </label>
              <input
                id="auth-email"
                type="email"
                className={`auth-form-input ${errors.email ? 'error' : ''}`}
                placeholder="Enter your email address"
                value={formData.email}
                onChange={(e) => handleInputChange('email', e.target.value)}
                disabled={isSubmitting || isLoading}
                autoComplete="email"
              />
              {errors.email && (
                <div className="auth-form-error">
                  <svg width="12" height="12" viewBox="0 0 12 12" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M6 11A5 5 0 1 1 6 1a5 5 0 0 1 0 10zM6 3v3M6 8h.01" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
                  </svg>
                  {errors.email}
                </div>
              )}
            </div>

            {/* Password Field */}
            <div className="auth-form-group">
              <label htmlFor="auth-password" className="auth-form-label">
                Password
              </label>
              <div className="auth-password-container">
                <input
                  id="auth-password"
                  type={showPassword ? 'text' : 'password'}
                  className={`auth-form-input ${errors.password ? 'error' : ''}`}
                  placeholder="Enter your password"
                  value={formData.password}
                  onChange={(e) => handleInputChange('password', e.target.value)}
                  disabled={isSubmitting || isLoading}
                  autoComplete={mode === 'signin' ? 'current-password' : 'new-password'}
                />
                <button
                  type="button"
                  className="auth-password-toggle"
                  onClick={() => setShowPassword(!showPassword)}
                  aria-label={showPassword ? 'Hide password' : 'Show password'}
                >
                  {showPassword ? (
                    <svg width="16" height="16" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">
                      <path d="M13.359 10.359A7.978 7.978 0 0 0 16 6.4c-1.007-1.993-3.673-4.8-8-4.8a8.968 8.968 0 0 0-2.347.312M6.4 6.4a1.6 1.6 0 1 1 3.2 0 1.6 1.6 0 0 1-3.2 0zM2.641 5.641A7.978 7.978 0 0 0 0 6.4c1.007 1.993 3.673 4.8 8 4.8a8.968 8.968 0 0 0 2.347-.312M1.6 1.6l12.8 12.8" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
                    </svg>
                  ) : (
                    <svg width="16" height="16" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">
                      <path d="M0 6.4C1.007 4.407 3.673 1.6 8 1.6s6.993 2.807 8 4.8c-1.007 1.993-3.673 4.8-8 4.8S1.007 8.393 0 6.4z" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
                      <circle cx="8" cy="6.4" r="1.6" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
                    </svg>
                  )}
                </button>
              </div>
              {errors.password && (
                <div className="auth-form-error">
                  <svg width="12" height="12" viewBox="0 0 12 12" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M6 11A5 5 0 1 1 6 1a5 5 0 0 1 0 10zM6 3v3M6 8h.01" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
                  </svg>
                  {errors.password}
                </div>
              )}
              {mode === 'signup' && !errors.password && (
                <div className="auth-password-requirements">
                  <small>Password must be at least 8 characters long</small>
                </div>
              )}
            </div>

            {/* Confirm Password Field (Signup only) */}
            {mode === 'signup' && (
              <div className="auth-form-group">
                <label htmlFor="auth-confirm-password" className="auth-form-label">
                  Confirm Password
                </label>
                <div className="auth-password-container">
                  <input
                    id="auth-confirm-password"
                    type={showConfirmPassword ? 'text' : 'password'}
                    className={`auth-form-input ${errors.confirmPassword ? 'error' : ''}`}
                    placeholder="Confirm your password"
                    value={formData.confirmPassword}
                    onChange={(e) => handleInputChange('confirmPassword', e.target.value)}
                    disabled={isSubmitting || isLoading}
                    autoComplete="new-password"
                  />
                  <button
                    type="button"
                    className="auth-password-toggle"
                    onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                    aria-label={showConfirmPassword ? 'Hide password confirmation' : 'Show password confirmation'}
                  >
                    {showConfirmPassword ? (
                      <svg width="16" height="16" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <path d="M13.359 10.359A7.978 7.978 0 0 0 16 6.4c-1.007-1.993-3.673-4.8-8-4.8a8.968 8.968 0 0 0-2.347.312M6.4 6.4a1.6 1.6 0 1 1 3.2 0 1.6 1.6 0 0 1-3.2 0zM2.641 5.641A7.978 7.978 0 0 0 0 6.4c1.007 1.993 3.673 4.8 8 4.8a8.968 8.968 0 0 0 2.347-.312M1.6 1.6l12.8 12.8" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
                      </svg>
                    ) : (
                      <svg width="16" height="16" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <path d="M0 6.4C1.007 4.407 3.673 1.6 8 1.6s6.993 2.807 8 4.8c-1.007 1.993-3.673 4.8-8 4.8S1.007 8.393 0 6.4z" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
                        <circle cx="8" cy="6.4" r="1.6" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
                      </svg>
                    )}
                  </button>
                </div>
                {errors.confirmPassword && (
                  <div className="auth-form-error">
                    <svg width="12" height="12" viewBox="0 0 12 12" fill="none" xmlns="http://www.w3.org/2000/svg">
                      <path d="M6 11A5 5 0 1 1 6 1a5 5 0 0 1 0 10zM6 3v3M6 8h.01" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
                    </svg>
                    {errors.confirmPassword}
                  </div>
                )}
              </div>
            )}

            {/* Terms Agreement (Signup only) */}
            {mode === 'signup' && (
              <div className="auth-form-group">
                <label className="auth-checkbox-label">
                  <input
                    type="checkbox"
                    checked={formData.agreeToTerms}
                    onChange={(e) => handleInputChange('agreeToTerms', e.target.checked)}
                    disabled={isSubmitting || isLoading}
                  />
                  <div className="auth-checkbox-custom"></div>
                  <span>
                    I agree to the <button type="button" className="auth-link-button">Terms of Service</button> and <button type="button" className="auth-link-button">Privacy Policy</button>
                  </span>
                </label>
                {errors.agreeToTerms && (
                  <div className="auth-form-error">
                    <svg width="12" height="12" viewBox="0 0 12 12" fill="none" xmlns="http://www.w3.org/2000/svg">
                      <path d="M6 11A5 5 0 1 1 6 1a5 5 0 0 1 0 10zM6 3v3M6 8h.01" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
                    </svg>
                    {errors.agreeToTerms}
                  </div>
                )}
              </div>
            )}

            {/* Submit Button */}
            <button
              type="submit"
              className="auth-form-submit"
              disabled={isSubmitting || isLoading}
            >
              {(isSubmitting || isLoading) ? (
                <div className="auth-loading-spinner">
                  <svg width="20" height="20" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M10 2V6M10 14V18M18 10H14M6 10H2M15.657 4.343L12.828 7.172M7.172 12.828L4.343 15.657M15.657 15.657L12.828 12.828M7.172 7.172L4.343 4.343" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                  </svg>
                  <span>{mode === 'signin' ? 'Signing In...' : 'Creating Account...'}</span>
                </div>
              ) : (
                <>
                  {mode === 'signin' ? (
                    <>
                      <svg width="16" height="16" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <path d="M6 2H4a2 2 0 0 0-2 2v8a2 2 0 0 0 2 2h2M10 12l4-4-4-4M14 8H6" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                      </svg>
                      Sign In
                    </>
                  ) : (
                    <>
                      <svg width="16" height="16" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <path d="M8 1v14M1 8h14" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                      </svg>
                      Create Account
                    </>
                  )}
                </>
              )}
            </button>
          </form>

          {/* Mode Switch */}
          <div className="auth-mode-switch">
            <p>
              {mode === 'signin' ? "Don't have an account? " : "Already have an account? "}
              <button
                type="button"
                className="auth-link-button"
                onClick={() => setMode(mode === 'signin' ? 'signup' : 'signin')}
                disabled={isSubmitting || isLoading}
              >
                {mode === 'signin' ? 'Sign Up' : 'Sign In'}
              </button>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AuthModal; 