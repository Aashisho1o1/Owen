import React from 'react';

interface FormFieldProps {
  label: string;
  children: React.ReactNode;
  error?: string;
  htmlFor?: string;
  required?: boolean;
}

/**
 * Reusable FormField component that wraps form inputs with consistent styling,
 * error handling, and accessibility features.
 * 
 * Based on React Hook Form best practices for reusable field components.
 */
export const FormField: React.FC<FormFieldProps> = ({ 
  label, 
  children, 
  error, 
  htmlFor, 
  required = false 
}) => {
  // Extract ID from child element if not provided
  const getChildId = (children: React.ReactNode): string | undefined => {
    const child = React.Children.only(children) as React.ReactElement;
    return child?.props?.id;
  };

  const fieldId = htmlFor || getChildId(children);

  return (
    <div className="auth-form-group">
      <label htmlFor={fieldId} className="auth-form-label">
        {label}
        {required && <span className="required-asterisk" aria-label="required">*</span>}
      </label>
      
      {children}
      
      {error && (
        <div className="auth-form-error" role="alert">
          <svg width="12" height="12" viewBox="0 0 12 12" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M6 11A5 5 0 1 1 6 1a5 5 0 0 1 0 10zM6 3v3M6 8h.01" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
          </svg>
          {error}
        </div>
      )}
    </div>
  );
}; 
 