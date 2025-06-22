import React, { useState, useEffect } from 'react';
import { ModalContainer, AuthForm } from './auth';
import { AuthMode } from './auth/useAuthFormValidation';

interface AuthModalProps {
  isOpen: boolean;
  onClose: () => void;
  initialMode?: AuthMode;
}

const AuthModal: React.FC<AuthModalProps> = ({ 
  isOpen, 
  onClose, 
  initialMode = 'signin' 
}) => {
  const [mode, setMode] = useState<AuthMode>(initialMode);

  // Reset mode when modal opens with different initial mode
  useEffect(() => {
    if (isOpen && initialMode !== mode) {
      setMode(initialMode);
    }
  }, [isOpen, initialMode]);

  // Handle successful authentication
  const handleSuccess = () => {
    onClose();
  };

  // Handle mode changes (signin ↔ signup)
  const handleModeChange = (newMode: AuthMode) => {
    setMode(newMode);
  };

  return (
    <ModalContainer
      isOpen={isOpen}
      onClose={onClose}
      title={mode === 'signin' ? 'Welcome Back' : 'Create Account'}
    >
      <AuthForm
        mode={mode}
        onSuccess={handleSuccess}
        onModeChange={handleModeChange}
      />
    </ModalContainer>
  );
};

export default AuthModal; 