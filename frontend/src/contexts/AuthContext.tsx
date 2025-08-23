import React, {
  createContext,
  useContext,
  useEffect,
  ReactNode,
  useCallback,
} from 'react';
import axios from 'axios';
import { logger } from '../utils/logger';
import { useSafeState } from '../hooks/useSafeState';
// Note: Auth functions are implemented within this context
// import { getStoredTokens } from '../services/api/auth';

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
  createGuestSession: () => Promise<boolean>;  // NEW: Guest session creation
  logout: () => void;
  updateProfile: (data: { display_name?: string; email?: string }) => Promise<boolean>;
  changePassword: (currentPassword: string, newPassword: string) => Promise<boolean>;
  refreshToken: () => Promise<boolean>;
  clearError: () => void;
}

// Create context
const AuthContext = createContext<AuthContextType | undefined>(undefined);

// API Configuration - MUST be defined in .env file
const rawApiUrl = import.meta.env.VITE_API_URL;

// Validate environment variable is loaded
if (!rawApiUrl) {
  console.error('❌ CRITICAL: VITE_API_URL is not defined in AuthContext');
  throw new Error('VITE_API_URL environment variable is required but not defined');
}

const API_URL = rawApiUrl.endsWith('/') ? rawApiUrl.slice(0, -1) : rawApiUrl;

// Debug log to show which API URL is being used
console.log('🌐 AuthContext API Configuration:', { 
  VITE_API_URL: import.meta.env.VITE_API_URL,
  API_BASE_URL: API_URL,
  mode: import.meta.env.MODE,
  env_loaded: !!import.meta.env.VITE_API_URL
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
  // DEBUG: Track AuthProvider instances
  const instanceId = React.useRef(Math.random().toString(36).substr(2, 9));
  console.log(`🔍 AuthProvider Instance Created: ${instanceId.current}`);
  
  const [user, setUser] = useSafeState<UserProfile | null>(null);
  const [isAuthenticated, setIsAuthenticated] = useSafeState(false);
  const [isLoading, setIsLoading] = useSafeState(true);
  const [error, setError] = useSafeState<string | null>(null);
  const [isInitialized, setIsInitialized] = useSafeState(false);

  // Token management
  // 🔒 SECURITY NOTE: localStorage is vulnerable to XSS attacks
  // In production, consider using httpOnly cookies for refresh tokens
  const getStoredTokens = useCallback((): AuthTokens | null => {
    try {
      const accessToken = localStorage.getItem('owen_access_token');
      const refreshToken = localStorage.getItem('owen_refresh_token');
      const tokenType = localStorage.getItem('owen_token_type') || 'bearer';
      const expiresAt = localStorage.getItem('owen_token_expires');

      if (accessToken && refreshToken) {
        return {
          access_token: accessToken,
          refresh_token: refreshToken,
          token_type: tokenType,
          expires_in: expiresAt ? Math.max(0, Math.floor((parseInt(expiresAt) - Date.now()) / 1000)) : 0,
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
      localStorage.setItem('owen_token_expires', (Date.now() + tokens.expires_in * 1000).toString());
      
      // Set axios default auth header
      apiInstance.defaults.headers.common['Authorization'] = `${tokens.token_type} ${tokens.access_token}`;
    } catch (err) {
      logger.error('Error storing tokens:', err);
    }
  }, []);

  const clearTokens = useCallback(() => {
    try {
      // Clear current tokens
      localStorage.removeItem('owen_access_token');
      localStorage.removeItem('owen_refresh_token');
      localStorage.removeItem('owen_token_type');
      localStorage.removeItem('owen_token_expires');
      
      // Clear any legacy tokens
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      localStorage.removeItem('token_type');
      localStorage.removeItem('expires_at');
      localStorage.removeItem('owen_expires_in'); // Remove old key format
      
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
        status: (err as any)?.response?.status,
        statusText: (err as any)?.response?.statusText,
        data: (err as any)?.response?.data
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
        const originalRequest = (err as any).config;

        // CRITICAL FIX: Don't attempt token refresh for login/register/refresh endpoints
        const isAuthEndpoint = originalRequest.url && (
          originalRequest.url.includes('/api/auth/login') ||
          originalRequest.url.includes('/api/auth/register') ||
          originalRequest.url.includes('/api/auth/refresh')
        );

        // Prevent infinite loops and skip auth endpoints
        if (err.response?.status === 401 && !originalRequest._retry && !isAuthEndpoint) {
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

  // Initialize authentication state - FIXED: Remove problematic dependencies
  useEffect(() => {
    const initializeAuth = async () => {
      if (isInitialized) return; // Prevent multiple initializations
      setIsInitialized(true);
      
      console.log(`🚀 [${instanceId.current}] Initializing authentication...`);
      setIsLoading(true);
      
      try {
        const tokens = getStoredTokens();
        if (tokens) {
          console.log('🔍 Found stored tokens, validating...');
          
          // Try to get user profile to verify token validity
          const success = await loadUserProfile();
          if (!success) {
            console.log('⚠️ Token validation failed, clearing all tokens');
            clearTokens();
            setUser(null);
            setIsAuthenticated(false);
          } else {
            console.log('✅ Token validation successful');
          }
        } else {
          console.log('ℹ️ No stored tokens found');
        }
      } catch (error) {
        console.error('❌ Auth initialization error:', error);
        clearTokens();
        setUser(null);
        setIsAuthenticated(false);
      } finally {
        setIsLoading(false);
        console.log('✅ Authentication initialization complete');
      }
    };

    initializeAuth();
  }, []); // CRITICAL FIX: Empty dependency array - run only once on mount

  // Add token expiration listener
  useEffect(() => {
    let isHandlingExpiration = false;
    
    const handleTokenExpiration = () => {
      if (isHandlingExpiration) {
        console.log('🔐 AuthContext: Token expiration already being handled, skipping...');
        return;
      }
      
      isHandlingExpiration = true;
      console.log('🔐 AuthContext: Token expired event received, logging out user');
      
      // Set user to null immediately to prevent multiple calls
      setUser(null);
      setIsAuthenticated(false);
      
      // Clear tokens without making API call since tokens are already invalid
      localStorage.removeItem('owen_access_token');
      localStorage.removeItem('owen_refresh_token');
      localStorage.removeItem('owen_token_type');
      localStorage.removeItem('owen_token_expires');
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      localStorage.removeItem('token_type');
      localStorage.removeItem('expires_at');
      localStorage.removeItem('owen_expires_in'); // Remove old key format
      
      // Reset expiration handling flag after a short delay
      setTimeout(() => {
        isHandlingExpiration = false;
      }, 1000);
    };

    window.addEventListener('auth:token-expired', handleTokenExpiration);
    return () => window.removeEventListener('auth:token-expired', handleTokenExpiration);
  }, []); // Remove logout dependency to prevent re-registration

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
      console.log('🔐 STEP 1: Making login API request...');
      const response = await apiInstance.post('/api/auth/login', data);
      console.log('🔐 STEP 2: ✅ Login API request successful:', response.data);
      
      const { access_token, refresh_token, token_type, expires_in, user: userProfile } = response.data;

      console.log('🔐 STEP 3: Storing tokens...');
      // Store tokens
      storeTokens({ access_token, refresh_token, token_type, expires_in });
      console.log('🔐 STEP 3: ✅ Tokens stored successfully');
      
      console.log('🔐 STEP 4: Setting user data...');
      // Set user data
      setUser(userProfile);
      setIsAuthenticated(true);
      console.log('🔐 STEP 4: ✅ User data set successfully');
      
      logger.log('Login successful', { username: userProfile.username });
      console.log('🔐 STEP 5: ✅ Login completed successfully');
      return true;
    } catch (err) {
      console.error('🔐 ❌ Login failed at step:', {
        error: err,
        status: (err as any)?.response?.status,
        statusText: (err as any)?.response?.statusText,
        data: (err as any)?.response?.data,
        config: (err as any)?.config,
        url: (err as any)?.config?.url,
        method: (err as any)?.config?.method
      });
      
      // Handle detailed error messages from backend
      let errorMessage = 'Login failed. Please try again.';
      
      if (axios.isAxiosError(err) && err.response?.data?.detail) {
        const detail = err.response.data.detail;
        
        // Check if it's a detailed validation error
        if (typeof detail === 'object' && detail.validation_errors) {
          // Extract the most relevant error message
          const validationErrors = detail.validation_errors;
          if (validationErrors.length > 0) {
            errorMessage = validationErrors[0].message;
          } else if (detail.message) {
            errorMessage = detail.message;
          }
        } else if (typeof detail === 'string') {
          errorMessage = detail;
        }
      }
      
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
        status: (err as any)?.response?.status,
        statusText: (err as any)?.response?.statusText,
        data: (err as any)?.response?.data,
        config: (err as any)?.config
      });
      
      // Handle detailed error messages from backend
      let errorMessage = 'Registration failed. Please try again.';
      
      if (axios.isAxiosError(err) && err.response?.data?.detail) {
        const detail = err.response.data.detail;
        
        // Check if it's a detailed validation error
        if (typeof detail === 'object' && detail.validation_errors) {
          // Extract the most relevant error message
          const validationErrors = detail.validation_errors;
          if (validationErrors.length > 0) {
            errorMessage = validationErrors[0].message;
          } else if (detail.message) {
            errorMessage = detail.message;
          }
        } else if (typeof detail === 'string') {
          errorMessage = detail;
        }
      }
      
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
          ? (err.response.data as any).detail
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
          ? (err.response.data as any).detail
          : 'Failed to change password.';
      setError(errorMessage);
      logger.error('Password change error:', err);
      return false;
    }
  };

  const createGuestSession = async (): Promise<boolean> => {
    setIsLoading(true);
    setError(null);
    
    // Debug logging
    console.log('🎯 Guest session creation:', { 
      apiUrl: API_URL,
      fullUrl: `${API_URL}/api/auth/guest`
    });
    
    try {
      console.log('🎯 STEP 1: Making guest session API request...');
      const response = await apiInstance.post('/api/auth/guest');
      console.log('🎯 STEP 2: ✅ Guest session API request successful:', response.data);
      
      const { access_token, token_type, expires_in, user: userProfile } = response.data;

      console.log('🎯 STEP 3: Storing guest tokens...');
      // Store tokens (no refresh token for guests)
      storeTokens({ 
        access_token, 
        refresh_token: '', // Guests don't get refresh tokens
        token_type, 
        expires_in 
      });
      console.log('🎯 STEP 3: ✅ Guest tokens stored successfully');
      
      console.log('🎯 STEP 4: Setting guest user data...');
      // Set user data (includes guest-specific info)
      setUser({
        ...userProfile,
        preferences: {
          onboarding_completed: true, // Skip onboarding for guests
          user_corrections: [],
          writing_style_profile: {},
          writing_type: 'fiction',
          feedback_style: 'constructive',
          primary_goal: 'try_features'
        },
        onboarding_completed: true
      });
      setIsAuthenticated(true);
      console.log('🎯 STEP 4: ✅ Guest user data set successfully');
      
      logger.log('Guest session created successfully', { 
        username: userProfile.username,
        sessionType: 'guest',
        expiresIn: expires_in 
      });
      console.log('🎯 STEP 5: ✅ Guest session completed successfully');
      return true;
    } catch (err) {
      console.error('🎯 ❌ Guest session creation failed:', {
        error: err,
        status: (err as any)?.response?.status,
        statusText: (err as any)?.response?.statusText,
        data: (err as any)?.response?.data,
        config: (err as any)?.config,
        url: (err as any)?.config?.url,
        method: (err as any)?.config?.method
      });
      
      const errorMessage =
        axios.isAxiosError(err) && err.response?.data?.detail
          ? (err.response.data as any).detail
          : 'Failed to create guest session. Please try again.';
      setError(errorMessage);
      logger.error('Guest session creation error:', err);
      return false;
    } finally {
      setIsLoading(false);
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
    createGuestSession,
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