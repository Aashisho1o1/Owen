import { useState, useCallback } from 'react';

export interface FormData {
  name: string;
  email: string;
  password: string;
  confirmPassword: string;
  agreeToTerms: boolean;
}

export interface FormErrors {
  name?: string;
  email?: string;
  password?: string;
  confirmPassword?: string;
  agreeToTerms?: string;
  submit?: string;
}

export type AuthMode = 'signin' | 'signup';

// Email validation regex - moved outside component for performance
const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

/**
 * Custom hook for handling authentication form validation logic.
 * Separates validation concerns from UI components for better testability and reusability.
 */
export const useAuthFormValidation = () => {
  const [errors, setErrors] = useState<FormErrors>({});

  /**
   * Validate individual field
   */
  const validateField = useCallback((field: keyof FormData, value: string | boolean, mode: AuthMode, allData?: FormData): string | undefined => {
    switch (field) {
      case 'name':
        if (mode === 'signup') {
          if (!String(value).trim()) {
            return 'Name is required';
          }
          if (String(value).trim().length < 2) {
            return 'Name must be at least 2 characters long';
          }
        }
        break;

      case 'email':
        if (!String(value).trim()) {
          return 'Email is required';
        }
        if (!emailRegex.test(String(value))) {
          return 'Please enter a valid email address';
        }
        break;

      case 'password':
        if (!String(value)) {
          return 'Password is required';
        }
        if (mode === 'signup') {
          // Detailed password validation for signup
          const password = String(value);
          const issues = [];
          
          if (password.length < 8) {
            issues.push('be at least 8 characters long');
          }
          
          if (!/[A-Z]/.test(password)) {
            issues.push('contain at least one uppercase letter (A-Z)');
          }
          
          if (!/[a-z]/.test(password)) {
            issues.push('contain at least one lowercase letter (a-z)');
          }
          
          if (!/[0-9]/.test(password)) {
            issues.push('contain at least one number (0-9)');
          }
          
          // Check for common weak passwords
          const weakPasswords = [
            'password', '12345678', 'qwerty123', 'abc12345', 'password123',
            '11111111', '87654321', 'qwertyui', 'password1', '123456789'
          ];
          
          if (weakPasswords.includes(password.toLowerCase())) {
            issues.push('not be a commonly used password');
          }
          
          if (issues.length > 0) {
            if (issues.length === 1) {
              return `Password must ${issues[0]}`;
            } else if (issues.length === 2) {
              return `Password must ${issues[0]} and ${issues[1]}`;
            } else {
              return `Password must ${issues.slice(0, -1).join(', ')}, and ${issues[issues.length - 1]}`;
            }
          }
        } else {
          // Simple validation for login
          if (String(value).length < 8) {
            return 'Password must be at least 8 characters long';
          }
        }
        break;

      case 'confirmPassword':
        if (mode === 'signup') {
          if (!String(value)) {
            return 'Please confirm your password';
          }
          if (allData && String(value) !== allData.password) {
            return 'Passwords do not match';
          }
        }
        break;

      case 'agreeToTerms':
        if (mode === 'signup' && !value) {
          return 'Please agree to the terms and conditions';
        }
        break;

      default:
        break;
    }
    
    return undefined;
  }, []);

  /**
   * Validate entire form
   */
  const validateForm = useCallback((formData: FormData, mode: AuthMode): boolean => {
    const newErrors: FormErrors = {};

    // Validate all relevant fields based on mode
    const fieldsToValidate: (keyof FormData)[] = mode === 'signin' 
      ? ['email', 'password']
      : ['name', 'email', 'password', 'confirmPassword', 'agreeToTerms'];

    fieldsToValidate.forEach(field => {
      const error = validateField(field, formData[field], mode, formData);
      if (error) {
        newErrors[field] = error;
      }
    });

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  }, [validateField]);

  /**
   * Clear specific field error
   */
  const clearFieldError = useCallback((field: keyof FormErrors) => {
    setErrors(prev => ({ ...prev, [field]: undefined }));
  }, []);

  /**
   * Set submission error
   */
  const setSubmitError = useCallback((error: string) => {
    setErrors(prev => ({ ...prev, submit: error }));
  }, []);

  /**
   * Clear all errors
   */
  const clearErrors = useCallback(() => {
    setErrors({});
  }, []);

  /**
   * Real-time field validation (for onBlur or onChange)
   */
  const validateFieldRealTime = useCallback((field: keyof FormData, value: string | boolean, mode: AuthMode, allData?: FormData) => {
    const error = validateField(field, value, mode, allData);
    setErrors(prev => ({ ...prev, [field]: error }));
    return !error;
  }, [validateField]);

  return {
    errors,
    validateForm,
    validateFieldRealTime,
    clearFieldError,
    setSubmitError,
    clearErrors
  };
}; 
 