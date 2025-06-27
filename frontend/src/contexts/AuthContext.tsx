import React, {
  createContext,
  useContext,
  useState,
  useEffect,
  ReactNode,
  useCallback,
} from 'react';
import axios from 'axios';
import { logger } from '../utils/logger';
import { 
  loginUser, 
  registerUser, 
  logoutUser, 
  getUserProfile, 
  setAuthTokens, 
  clearAuthTokens, 
  getStoredTokens, 
  isTokenExpired 
} from '../services/api/auth';

// Types for authentication
interface UserProfile {
  user_id: string;
  username: string;
  email: string;
  display_name?: string;
  created_at: string;
  preferences: {
    onboarding_completed: boolean;
    user_corrections: string[];
    writing_style_profile?: Record<string, unknown>;
    writing_type?: string;
    feedback_style?: string;
    primary_goal?: string;
  };
  onboarding_completed: boolean;
}

interface AuthTokens {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
}

interface LoginData {
  email: string;
  password: string;
  remember_me?: boolean;
}

interface RegisterData {
  email: string;
  password: string;
  name: string;
}

interface AuthContextType {
  // State
  user: UserProfile | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
  
  // Actions
  login: (data: LoginData) => Promise<boolean>;
  register: (data: RegisterData) => Promise<boolean>;
  logout: () => void;
  updateProfile: (data: { display_name?: string; email?: string }) => Promise<boolean>;
  changePassword: (currentPassword: string, newPassword: string) => Promise<boolean>;
  refreshToken: () => Promise<boolean>;
  clearError: () => void;
}

// Create context
const AuthContext = createContext<AuthContextType | undefined>(undefined);

// API Configuration
const rawApiUrl = import.meta.env.VITE_API_URL || 'https://backend-copy-production-95b5.up.railway.app';
const API_URL = rawApiUrl.startsWith('http') ? rawApiUrl : `https://${rawApiUrl}`;

// Debug log to show which API URL is being used
console.log('🌐 API Configuration:', { 
  VITE_API_URL: import.meta.env.VITE_API_URL,
  API_BASE_URL: API_URL,
  mode: import.meta.env.MODE
});

// Configure axios instance
const apiInstance = axios.create({
  baseURL: API_URL,
  timeout: 10000,
  // 🔒 Security headers
  headers: {
    'Content-Type': 'application/json',
    'X-Requested-With': 'XMLHttpRequest', // Helps prevent CSRF
  },
});

// Auth provider component
export const AuthProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<UserProfile | null>(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Token management
  // 🔒 SECURITY NOTE: localStorage is vulnerable to XSS attacks
  // In production, consider using httpOnly cookies for refresh tokens
  const getStoredTokens = useCallback((): AuthTokens | null => {
    try {
      const accessToken = localStorage.getItem('owen_access_token');
      const refreshToken = localStorage.getItem('owen_refresh_token');
      const tokenType = localStorage.getItem('owen_token_type') || 'bearer';
      const expiresIn = localStorage.getItem('owen_expires_in');

      if (accessToken && refreshToken) {
        return {
          access_token: accessToken,
          refresh_token: refreshToken,
          token_type: tokenType,
          expires_in: expiresIn ? parseInt(expiresIn) : 0,
        };
      }
      return null;
    } catch (err) {
      logger.error('Error getting stored tokens:', err);
      return null;
    }
  }, []);

  const storeTokens = useCallback((tokens: AuthTokens) => {
    try {
      localStorage.setItem('owen_access_token', tokens.access_token);
      localStorage.setItem('owen_refresh_token', tokens.refresh_token);
      localStorage.setItem('owen_token_type', tokens.token_type);
      localStorage.setItem('owen_expires_in', tokens.expires_in.toString());
      
      // Set axios default auth header
      apiInstance.defaults.headers.common['Authorization'] = `${tokens.token_type} ${tokens.access_token}`;
    } catch (err) {
      logger.error('Error storing tokens:', err);
    }
  }, []);

  const clearTokens = useCallback(() => {
    try {
      localStorage.removeItem('owen_access_token');
      localStorage.removeItem('owen_refresh_token');
      localStorage.removeItem('owen_token_type');
      localStorage.removeItem('owen_expires_in');
      delete apiInstance.defaults.headers.common['Authorization'];
    } catch (err) {
      logger.error('Error clearing tokens:', err);
    }
  }, []);

  const logout = useCallback(() => {
    // Call logout endpoint (fire-and-forget)
    apiInstance.post('/api/auth/logout').catch(() => {});

    // Clear local state and storage
    clearTokens();
    setUser(null);
    setIsAuthenticated(false);
    setError(null);

    logger.log('User logged out');
  }, [clearTokens]);

  const loadUserProfile = useCallback(async (): Promise<boolean> => {
    try {
      console.log('👤 Loading user profile...');
      const response = await apiInstance.get('/api/auth/profile');
      console.log('✅ User profile loaded:', response.data);
      setUser(response.data);
      setIsAuthenticated(true);
      setError(null);
      return true;
    } catch (err) {
      console.error('❌ Failed to load user profile:', {
        error: err,
        status: err?.response?.status,
        statusText: err?.response?.statusText,
        data: err?.response?.data
      });
      logger.error('Error loading user profile:', err);
      setUser(null);
      setIsAuthenticated(false);
      return false;
    }
  }, []);

  const refreshToken = useCallback(async (): Promise<boolean> => {
    const tokens = getStoredTokens();
    if (!tokens?.refresh_token) {
      console.log('❌ No refresh token available');
      return false;
    }

    try {
      console.log('🔄 Attempting token refresh...');
      const response = await apiInstance.post('/api/auth/refresh', {
        refresh_token: tokens.refresh_token,
      });

      const { access_token, token_type, expires_in } = response.data;
      
      // Update stored tokens (keep the same refresh token)
      storeTokens({
        access_token,
        refresh_token: tokens.refresh_token,
        token_type,
        expires_in,
      });

      console.log('✅ Token refresh successful');
      return true;
    } catch (err) {
      console.error('❌ Token refresh failed:', err);
      logger.error('Token refresh error:', err);
      // If refresh fails, log the user out as the session is invalid
      logout();
      return false;
    }
  }, [getStoredTokens, storeTokens, logout]);

  // Set up axios interceptor for token refresh
  useEffect(() => {
    const responseInterceptor = apiInstance.interceptors.response.use(
      (response) => response,
      async (err) => {
        const originalRequest = err.config;

        // Prevent infinite loops
        if (err.response?.status === 401 && !originalRequest._retry && originalRequest.url !== '/api/auth/refresh') {
          originalRequest._retry = true;

          console.log('🔄 Token expired, attempting refresh...');
          const success = await refreshToken();
          if (success) {
            const newTokens = getStoredTokens();
            if (newTokens) {
              originalRequest.headers['Authorization'] = `${newTokens.token_type} ${newTokens.access_token}`;
              console.log('✅ Token refreshed, retrying request');
              return apiInstance(originalRequest);
            }
          } else {
            console.log('❌ Token refresh failed, logging out');
            // Refresh failed, user will be logged out
          }
        }

        return Promise.reject(err);
      }
    );

    const requestInterceptor = apiInstance.interceptors.request.use(
      (config) => {
        const tokens = getStoredTokens();
        if (tokens && !config.headers['Authorization']) {
          config.headers['Authorization'] = `${tokens.token_type} ${tokens.access_token}`;
        }
        return config;
      },
      (error) => Promise.reject(error)
    );

    // Cleanup interceptors on unmount
    return () => {
      apiInstance.interceptors.response.eject(responseInterceptor);
      apiInstance.interceptors.request.eject(requestInterceptor);
    };
  }, [refreshToken, getStoredTokens]);

  // Initialize authentication state
  useEffect(() => {
    const initializeAuth = async () => {
      console.log('🚀 Initializing authentication...');
      setIsLoading(true);
      
      // TEMPORARY FIX: Clear potentially corrupted tokens to prevent refresh loops
      const tokens = getStoredTokens();
      if (tokens) {
        console.log('🔍 Found stored tokens, validating...');
        
        // Try to get user profile to verify token validity
        const success = await loadUserProfile();
        if (!success) {
          console.log('⚠️ Token validation failed, clearing all tokens to prevent loops');
            clearTokens();
          setUser(null);
          setIsAuthenticated(false);
        } else {
          console.log('✅ Token validation successful');
        }
      } else {
        console.log('📭 No stored tokens found');
      }
      setIsLoading(false);
    };

    initializeAuth();
  }, [getStoredTokens, loadUserProfile, clearTokens]);

  const login = async (data: LoginData): Promise<boolean> => {
    setIsLoading(true);
    setError(null);
    
    // Debug logging
    console.log('🔐 Login attempt:', { 
      email: data.email, 
      apiUrl: API_URL,
      fullUrl: `${API_URL}/api/auth/login`
    });
    
    try {
      const response = await apiInstance.post('/api/auth/login', data);
      console.log('✅ Login successful:', response.data);
      
      const { access_token, refresh_token, token_type, expires_in, user: userProfile } = response.data;

      // Store tokens
      storeTokens({ access_token, refresh_token, token_type, expires_in });
      
      // Set user data
      setUser(userProfile);
      setIsAuthenticated(true);
      
      logger.log('Login successful', { username: userProfile.username });
      return true;
    } catch (err) {
      console.error('❌ Login failed:', {
        error: err,
        status: err?.response?.status,
        statusText: err?.response?.statusText,
        data: err?.response?.data,
        config: err?.config
      });
      
      const errorMessage =
        axios.isAxiosError(err) && err.response?.data?.detail
          ? err.response.data.detail
          : 'Login failed. Please try again.';
      setError(errorMessage);
      logger.error('Login error:', err);
      return false;
    } finally {
      setIsLoading(false);
    }
  };

  const register = async (data: RegisterData): Promise<boolean> => {
    setIsLoading(true);
    setError(null);
    
    // Debug logging
    console.log('📝 Register attempt:', { 
      email: data.email, 
      name: data.name,
      apiUrl: API_URL,
      fullUrl: `${API_URL}/api/auth/register`
    });
    
    try {
      const response = await apiInstance.post('/api/auth/register', data);
      console.log('✅ Registration successful:', response.data);
      
      const { access_token, refresh_token, token_type, expires_in, user: userProfile } = response.data;

      // Store tokens
      storeTokens({ access_token, refresh_token, token_type, expires_in });
      
      // Set user data
      setUser(userProfile);
      setIsAuthenticated(true);
      
      logger.log('Registration successful', { username: userProfile.username });
      return true;
    } catch (err) {
      console.error('❌ Registration failed:', {
        error: err,
        status: err?.response?.status,
        statusText: err?.response?.statusText,
        data: err?.response?.data,
        config: err?.config
      });
      
      const errorMessage =
        axios.isAxiosError(err) && err.response?.data?.detail
          ? err.response.data.detail
          : 'Registration failed. Please try again.';
      setError(errorMessage);
      logger.error('Registration error:', err);
      return false;
    } finally {
      setIsLoading(false);
    }
  };

  const updateProfile = async (data: { display_name?: string; email?: string }): Promise<boolean> => {
    setError(null);
    
    try {
      const response = await apiInstance.put('/api/auth/profile', data);
      setUser(response.data);
      logger.log('Profile updated successfully');
      return true;
    } catch (err) {
      const errorMessage =
        axios.isAxiosError(err) && err.response?.data?.detail
          ? err.response.data.detail
          : 'Failed to update profile.';
      setError(errorMessage);
      logger.error('Profile update error:', err);
      return false;
    }
  };

  const changePassword = async (currentPassword: string, newPassword: string): Promise<boolean> => {
    setError(null);
    
    try {
      await apiInstance.post('/api/auth/change-password', {
        current_password: currentPassword,
        new_password: newPassword,
      });
      logger.log('Password changed successfully');
      return true;
    } catch (err) {
      const errorMessage =
        axios.isAxiosError(err) && err.response?.data?.detail
          ? err.response.data.detail
          : 'Failed to change password.';
      setError(errorMessage);
      logger.error('Password change error:', err);
      return false;
    }
  };

  const clearError = () => {
    setError(null);
  };

  const contextValue: AuthContextType = {
    user,
    isAuthenticated,
    isLoading,
    error,
    login,
    register,
    logout,
    updateProfile,
    changePassword,
    refreshToken,
    clearError,
  };

  return (
    <AuthContext.Provider value={contextValue}>
      {children}
    </AuthContext.Provider>
  );
};

// Custom hook to use auth context
export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};