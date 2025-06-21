import React, { createContext, useContext, useState, ReactNode } from 'react';
import { useAuth } from './AuthContext';

export interface UIContextType {
  // Authentication state (derived from AuthContext)
  isAuthenticated: boolean;
  user: any;

  // Auth Modal State
  showAuthModal: boolean;
  setShowAuthModal: React.Dispatch<React.SetStateAction<boolean>>;
  authMode: 'signin' | 'signup';
  setAuthMode: React.Dispatch<React.SetStateAction<'signin' | 'signup'>>;
}

const UIContext = createContext<UIContextType | undefined>(undefined);

export const UIProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  // Auth Modal State
  const [showAuthModal, setShowAuthModal] = useState(false);
  const [authMode, setAuthMode] = useState<'signin' | 'signup'>('signin');

  // Get authentication state from AuthContext
  const { user, isAuthenticated } = useAuth();

  // Build context value
  const value: UIContextType = {
    isAuthenticated,
    user,
    showAuthModal,
    setShowAuthModal,
    authMode,
    setAuthMode,
  };

  return <UIContext.Provider value={value}>{children}</UIContext.Provider>;
};

export const useUIContext = (): UIContextType => {
  const context = useContext(UIContext);
  if (context === undefined) {
    throw new Error('useUIContext must be used within a UIProvider');
  }
  return context;
}; 