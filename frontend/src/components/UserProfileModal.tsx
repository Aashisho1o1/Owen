import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';

interface UserProfileModalProps {
  isOpen: boolean;
  onClose: () => void;
}

interface ProfileFormData {
  display_name: string;
  email: string;
}

interface PasswordFormData {
  current_password: string;
  new_password: string;
  confirm_password: string;
}

interface FormErrors {
  display_name?: string;
  email?: string;
  current_password?: string;
  new_password?: string;
  confirm_password?: string;
}

const UserProfileModal: React.FC<UserProfileModalProps> = ({ isOpen, onClose }) => {
  const { user, updateProfile, changePassword, logout, error, clearError } = useAuth();
  const [activeTab, setActiveTab] = useState<'profile' | 'password'>('profile');
  const [isLoading, setIsLoading] = useState(false);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);
  
  // Profile form state
  const [profileData, setProfileData] = useState<ProfileFormData>({
    display_name: '',
    email: '',
  });
  
  // Password form state
  const [passwordData, setPasswordData] = useState<PasswordFormData>({
    current_password: '',
    new_password: '',
    confirm_password: '',
  });
  
  const [formErrors, setFormErrors] = useState<FormErrors>({});
  const [showPasswords, setShowPasswords] = useState({
    current: false,
    new: false,
    confirm: false,
  });

  // Initialize form data when modal opens
  useEffect(() => {
    if (isOpen && user) {
      setProfileData({
        display_name: user.display_name || '',
        email: user.email,
      });
      setPasswordData({
        current_password: '',
        new_password: '',
        confirm_password: '',
      });
      setFormErrors({});
      setSuccessMessage(null);
      clearError();
    }
  }, [isOpen, user, clearError]);

  // Clear success message and errors when switching tabs
  useEffect(() => {
    setSuccessMessage(null);
    setFormErrors({});
    clearError();
  }, [activeTab, clearError]);

  const validateProfileForm = (): boolean => {
    const errors: FormErrors = {};

    // Email validation
    if (!profileData.email.trim()) {
      errors.email = 'Email is required';
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(profileData.email)) {
      errors.email = 'Please enter a valid email address';
    }

    setFormErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const validatePasswordForm = (): boolean => {
    const errors: FormErrors = {};

    // Current password validation
    if (!passwordData.current_password) {
      errors.current_password = 'Current password is required';
    }

    // New password validation
    if (!passwordData.new_password) {
      errors.new_password = 'New password is required';
    } else if (passwordData.new_password.length < 8) {
      errors.new_password = 'Password must be at least 8 characters';
    } else if (!/(?=.*[a-zA-Z])(?=.*\d)/.test(passwordData.new_password)) {
      errors.new_password = 'Password must contain at least one letter and one number';
    }

    // Confirm password validation
    if (!passwordData.confirm_password) {
      errors.confirm_password = 'Please confirm your new password';
    } else if (passwordData.new_password !== passwordData.confirm_password) {
      errors.confirm_password = 'Passwords do not match';
    }

    // Check if new password is different from current
    if (passwordData.current_password === passwordData.new_password) {
      errors.new_password = 'New password must be different from current password';
    }

    setFormErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const handleProfileSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!validateProfileForm()) {
      return;
    }

    setIsLoading(true);
    setSuccessMessage(null);
    
    const success = await updateProfile({
      display_name: profileData.display_name || undefined,
      email: profileData.email,
    });

    if (success) {
      setSuccessMessage('Profile updated successfully!');
    }
    
    setIsLoading(false);
  };

  const handlePasswordSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!validatePasswordForm()) {
      return;
    }

    setIsLoading(true);
    setSuccessMessage(null);
    
    const success = await changePassword(passwordData.current_password, passwordData.new_password);

    if (success) {
      setSuccessMessage('Password changed successfully!');
      setPasswordData({
        current_password: '',
        new_password: '',
        confirm_password: '',
      });
    }
    
    setIsLoading(false);
  };

  const handleProfileInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setProfileData(prev => ({
      ...prev,
      [name]: value,
    }));
    
    // Clear field-specific errors
    if (formErrors[name as keyof FormErrors]) {
      setFormErrors(prev => ({
        ...prev,
        [name]: undefined,
      }));
    }
  };

  const handlePasswordInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setPasswordData(prev => ({
      ...prev,
      [name]: value,
    }));
    
    // Clear field-specific errors
    if (formErrors[name as keyof FormErrors]) {
      setFormErrors(prev => ({
        ...prev,
        [name]: undefined,
      }));
    }
  };

  const togglePasswordVisibility = (field: 'current' | 'new' | 'confirm') => {
    setShowPasswords(prev => ({
      ...prev,
      [field]: !prev[field],
    }));
  };

  const handleLogout = () => {
    logout();
    onClose();
  };

  if (!isOpen || !user) return null;

  return (
    <div className="auth-modal-overlay" onClick={onClose}>
      <div className="user-profile-modal" onClick={(e) => e.stopPropagation()}>
        <div className="auth-modal-header">
          <h2>Account Settings</h2>
          <button className="auth-modal-close" onClick={onClose} aria-label="Close">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <line x1="18" y1="6" x2="6" y2="18"></line>
              <line x1="6" y1="6" x2="18" y2="18"></line>
            </svg>
          </button>
        </div>

        <div className="profile-modal-content">
          {/* User info header */}
          <div className="user-info-header">
            <div className="user-avatar">
              {(user.display_name || user.username || 'U').charAt(0).toUpperCase()}
            </div>
            <div className="user-info-text">
              <h3>{user.display_name || user.username || 'Unknown User'}</h3>
              <p>@{user.username || 'unknown'}</p>
              <small>Member since {new Date(user.created_at).toLocaleDateString()}</small>
            </div>
          </div>

          {/* Tab navigation */}
          <div className="profile-tabs">
            <button
              className={`profile-tab ${activeTab === 'profile' ? 'active' : ''}`}
              onClick={() => setActiveTab('profile')}
            >
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path>
                <circle cx="12" cy="7" r="4"></circle>
              </svg>
              Profile
            </button>
            <button
              className={`profile-tab ${activeTab === 'password' ? 'active' : ''}`}
              onClick={() => setActiveTab('password')}
            >
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <rect x="3" y="11" width="18" height="11" rx="2" ry="2"></rect>
                <circle cx="12" cy="16" r="1"></circle>
                <path d="M7 11V7a5 5 0 0 1 10 0v4"></path>
              </svg>
              Password
            </button>
          </div>

          {/* Success message */}
          {successMessage && (
            <div className="auth-success-banner">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <polyline points="20,6 9,17 4,12"></polyline>
              </svg>
              {successMessage}
            </div>
          )}

          {/* Error message */}
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

          {/* Tab content */}
          {activeTab === 'profile' ? (
            <form onSubmit={handleProfileSubmit} className="auth-form">
              <div className="auth-form-group">
                <label htmlFor="display_name" className="auth-form-label">
                  Display Name
                </label>
                <input
                  type="text"
                  id="display_name"
                  name="display_name"
                  value={profileData.display_name}
                  onChange={handleProfileInputChange}
                  className="auth-form-input"
                  placeholder="How should we call you?"
                  disabled={isLoading}
                />
              </div>

              <div className="auth-form-group">
                <label htmlFor="email" className="auth-form-label">
                  Email Address
                </label>
                <input
                  type="email"
                  id="email"
                  name="email"
                  value={profileData.email}
                  onChange={handleProfileInputChange}
                  className={`auth-form-input ${formErrors.email ? 'error' : ''}`}
                  disabled={isLoading}
                />
                {formErrors.email && (
                  <span className="auth-form-error">{formErrors.email}</span>
                )}
              </div>

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
                  'Update Profile'
                )}
              </button>
            </form>
          ) : (
            <form onSubmit={handlePasswordSubmit} className="auth-form">
              <div className="auth-form-group">
                <label htmlFor="current_password" className="auth-form-label">
                  Current Password
                </label>
                <div className="auth-password-container">
                  <input
                    type={showPasswords.current ? 'text' : 'password'}
                    id="current_password"
                    name="current_password"
                    value={passwordData.current_password}
                    onChange={handlePasswordInputChange}
                    className={`auth-form-input ${formErrors.current_password ? 'error' : ''}`}
                    disabled={isLoading}
                  />
                  <button
                    type="button"
                    className="auth-password-toggle"
                    onClick={() => togglePasswordVisibility('current')}
                    disabled={isLoading}
                  >
                    {showPasswords.current ? '👁️‍🗨️' : '👁️'}
                  </button>
                </div>
                {formErrors.current_password && (
                  <span className="auth-form-error">{formErrors.current_password}</span>
                )}
              </div>

              <div className="auth-form-group">
                <label htmlFor="new_password" className="auth-form-label">
                  New Password
                </label>
                <div className="auth-password-container">
                  <input
                    type={showPasswords.new ? 'text' : 'password'}
                    id="new_password"
                    name="new_password"
                    value={passwordData.new_password}
                    onChange={handlePasswordInputChange}
                    className={`auth-form-input ${formErrors.new_password ? 'error' : ''}`}
                    disabled={isLoading}
                  />
                  <button
                    type="button"
                    className="auth-password-toggle"
                    onClick={() => togglePasswordVisibility('new')}
                    disabled={isLoading}
                  >
                    {showPasswords.new ? '👁️‍🗨️' : '👁️'}
                  </button>
                </div>
                {formErrors.new_password && (
                  <span className="auth-form-error">{formErrors.new_password}</span>
                )}
              </div>

              <div className="auth-form-group">
                <label htmlFor="confirm_password" className="auth-form-label">
                  Confirm New Password
                </label>
                <div className="auth-password-container">
                  <input
                    type={showPasswords.confirm ? 'text' : 'password'}
                    id="confirm_password"
                    name="confirm_password"
                    value={passwordData.confirm_password}
                    onChange={handlePasswordInputChange}
                    className={`auth-form-input ${formErrors.confirm_password ? 'error' : ''}`}
                    disabled={isLoading}
                  />
                  <button
                    type="button"
                    className="auth-password-toggle"
                    onClick={() => togglePasswordVisibility('confirm')}
                    disabled={isLoading}
                  >
                    {showPasswords.confirm ? '👁️‍🗨️' : '👁️'}
                  </button>
                </div>
                {formErrors.confirm_password && (
                  <span className="auth-form-error">{formErrors.confirm_password}</span>
                )}
              </div>

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
                  'Change Password'
                )}
              </button>
            </form>
          )}

          {/* Logout button */}
          <div className="profile-logout-section">
            <button
              type="button"
              className="profile-logout-button"
              onClick={handleLogout}
              disabled={isLoading}
            >
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"></path>
                <polyline points="16,17 21,12 16,7"></polyline>
                <line x1="21" y1="12" x2="9" y2="12"></line>
              </svg>
              Sign Out
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default UserProfileModal; 