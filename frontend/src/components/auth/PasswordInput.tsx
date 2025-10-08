import React, { useState } from 'react';

interface PasswordInputProps {
  id: string;
  value: string;
  onChange: (value: string) => void;
  onBlur?: () => void;
  placeholder?: string;
  disabled?: boolean;
  autoComplete?: string;
  className?: string;
  showRequirements?: boolean;
  'aria-describedby'?: string;
}

/**
 * Specialized PasswordInput component with visibility toggle functionality.
 * Handles password-specific UX patterns and accessibility requirements.
 */
export const PasswordInput: React.FC<PasswordInputProps> = ({
  id,
  value,
  onChange,
  onBlur,
  placeholder = "Enter your password",
  disabled = false,
  autoComplete = "current-password",
  className = "",
  showRequirements = false,
  'aria-describedby': ariaDescribedBy
}) => {
  const [showPassword, setShowPassword] = useState(false);

  const togglePasswordVisibility = () => {
    setShowPassword(!showPassword);
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    onChange(e.target.value);
  };

  return (
    <>
      <div className="auth-password-container">
        <input
          id={id}
          type={showPassword ? 'text' : 'password'}
          className={`auth-form-input ${className}`}
          placeholder={placeholder}
          value={value}
          onChange={handleChange}
          onBlur={onBlur}
          disabled={disabled}
          autoComplete={autoComplete}
          aria-describedby={ariaDescribedBy}
        />
        <button
          type="button"
          className="auth-password-toggle"
          onClick={togglePasswordVisibility}
          disabled={disabled}
          aria-label={showPassword ? 'Hide password' : 'Show password'}
          tabIndex={0}
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
      
      {showRequirements && (
        <div className="auth-password-requirements" id={`${id}-requirements`}>
          <small>
            Password must:
            <ul style={{ margin: '4px 0', paddingLeft: '16px', fontSize: '12px' }}>
              <li>Be at least 8 characters long</li>
              <li>Contain at least one uppercase letter (A-Z)</li>
              <li>Contain at least one lowercase letter (a-z)</li>
              <li>Contain at least one number (0-9)</li>
            </ul>
          </small>
        </div>
      )}
    </>
  );
}; 
 