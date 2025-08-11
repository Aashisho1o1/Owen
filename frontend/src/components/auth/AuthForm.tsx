import React, { useState, useEffect } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { FormField } from './FormField';
import { PasswordInput } from './PasswordInput';
import { useAuthFormValidation, FormData, AuthMode } from './useAuthFormValidation';

interface AuthFormProps {
  mode: AuthMode;
  onSuccess: () => void;
  onModeChange: (mode: AuthMode) => void;
}

/**
 * AuthForm component handles form logic and submission.
 * Uses specialized form components and validation hook for clean separation of concerns.
 */
export const AuthForm: React.FC<AuthFormProps> = ({ mode, onSuccess, onModeChange }) => {
  const { login, register, createGuestSession, isLoading, error: authError } = useAuth();
  const { 
    errors, 
    validateForm, 
    clearFieldError, 
    setSubmitError, 
    clearErrors 
  } = useAuthFormValidation();

  const [formData, setFormData] = useState<FormData>({
    name: '',
    email: '',
    password: '',
    confirmPassword: '',
    agreeToTerms: false
  });

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
    clearErrors();
  }, [mode, clearErrors]);

  // Handle input changes
  const handleInputChange = (field: keyof FormData, value: string | boolean) => {
    setFormData(prev => ({ ...prev, [field]: value }));
    
    // Clear specific field error when user starts typing
    if (errors[field]) {
      clearFieldError(field);
    }
  };

  // Handle form submission
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!validateForm(formData, mode)) {
      return;
    }

    setIsSubmitting(true);
    
    try {
      let success = false;
      
      if (mode === 'signin') {
        success = await login({
          email: formData.email,
          password: formData.password,
          remember_me: false
        });
      } else {
        success = await register({
          email: formData.email,
          password: formData.password,
          name: formData.name
        });
      }
      
      if (success) {
        onSuccess();
      }
    } catch (error) {
      console.error('Authentication error:', error);
      setSubmitError('Authentication failed. Please check your credentials.');
    } finally {
      setIsSubmitting(false);
    }
  };

  // Handle guest session creation
  const handleGuestSession = async () => {
    setIsSubmitting(true);
    
    try {
      const success = await createGuestSession();
      if (success) {
        onSuccess();
      }
    } catch (error) {
      console.error('Guest session error:', error);
      setSubmitError('Failed to create guest session. Please try again.');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
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
          <FormField 
            label="Full Name" 
            error={errors.name}
            htmlFor="auth-name"
            required
          >
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
          </FormField>
        )}

        {/* Email Field */}
        <FormField 
          label="Email Address" 
          error={errors.email}
          htmlFor="auth-email"
          required
        >
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
        </FormField>

        {/* Password Field */}
        <FormField 
          label="Password" 
          error={errors.password}
          htmlFor="auth-password"
          required
        >
          <PasswordInput
            id="auth-password"
            value={formData.password}
            onChange={(value) => handleInputChange('password', value)}
            disabled={isSubmitting || isLoading}
            autoComplete={mode === 'signin' ? 'current-password' : 'new-password'}
            className={errors.password ? 'error' : ''}
            showRequirements={mode === 'signup' && !errors.password}
            aria-describedby={mode === 'signup' ? 'auth-password-requirements' : undefined}
          />
        </FormField>

        {/* Confirm Password Field (Signup only) */}
        {mode === 'signup' && (
          <FormField 
            label="Confirm Password" 
            error={errors.confirmPassword}
            htmlFor="auth-confirm-password"
            required
          >
            <PasswordInput
              id="auth-confirm-password"
              value={formData.confirmPassword}
              onChange={(value) => handleInputChange('confirmPassword', value)}
              placeholder="Confirm your password"
              disabled={isSubmitting || isLoading}
              autoComplete="new-password"
              className={errors.confirmPassword ? 'error' : ''}
            />
          </FormField>
        )}

        {/* Terms Agreement (Signup only) */}
        {mode === 'signup' && (
          <FormField 
            label="" 
            error={errors.agreeToTerms}
          >
            <label className="auth-checkbox-label">
              <input
                type="checkbox"
                checked={formData.agreeToTerms}
                onChange={(e) => handleInputChange('agreeToTerms', e.target.checked)}
                disabled={isSubmitting || isLoading}
              />
              <div className="auth-checkbox-custom"></div>
              <span>
                I agree to the <button type="button" className="auth-link-button" onClick={() => window.open('https://docs.google.com/document/d/1m2qcsowK3b1TRXi1LwOBP3tNNPpUlYG-iFQond9mZas/edit?usp=sharing', '_blank', 'noopener,noreferrer')}>Terms of Service</button> and <button type="button" className="auth-link-button" onClick={() => window.open('https://docs.google.com/document/d/17dKWwfxF4QaA8Qg3DfiiXjjUukYVigIWRlAr0vPOvGg/edit?usp=sharing', '_blank', 'noopener,noreferrer')}>Privacy Policy</button>
              </span>
            </label>
          </FormField>
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

      {/* Guest Access Section */}
      <div className="auth-divider">
        <div className="auth-divider-line"></div>
        <span className="auth-divider-text">or</span>
        <div className="auth-divider-line"></div>
      </div>

      <button
        type="button"
        className="auth-guest-button"
        onClick={handleGuestSession}
        disabled={isSubmitting || isLoading}
      >
        {(isSubmitting || isLoading) ? (
          <div className="auth-loading-spinner">
            <svg width="20" height="20" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M10 2V6M10 14V18M18 10H14M6 10H2M15.657 4.343L12.828 7.172M7.172 12.828L4.343 15.657M15.657 15.657L12.828 12.828M7.172 7.172L4.343 4.343" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
            </svg>
            <span>Creating Guest Session...</span>
          </div>
        ) : (
          <>
            <svg width="16" height="16" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M8 2l2.5 2.5L8 7M2 8h12M8 14l-2.5-2.5L8 9" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
            </svg>
            <div className="auth-guest-button-content">
              <span className="auth-guest-button-title">Try Without Account</span>
              <span className="auth-guest-button-subtitle">Experience all features • No email required • 24-hour trial</span>
            </div>
          </>
        )}
      </button>

      {/* Mode Switch */}
      <div className="auth-mode-switch">
        <p>
          {mode === 'signin' ? "Don't have an account? " : "Already have an account? "}
          <button
            type="button"
            className="auth-link-button"
            onClick={() => onModeChange(mode === 'signin' ? 'signup' : 'signin')}
            disabled={isSubmitting || isLoading}
          >
            {mode === 'signin' ? 'Sign Up' : 'Sign In'}
          </button>
        </p>
      </div>
    </div>
  );
}; 
 