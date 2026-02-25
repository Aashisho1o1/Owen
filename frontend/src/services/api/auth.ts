/**
 * Authentication API Service
 * Handles all authentication-related API calls.
 */

import apiClient from './client';
import {
  LoginRequest,
  RegisterRequest,
  TokenResponse,
  UserProfile
} from './types';
import { logger } from '../../utils/logger';

// === AUTHENTICATION ENDPOINTS ===

export const loginUser = async (credentials: LoginRequest): Promise<TokenResponse> => {
  const response = await apiClient.post('/api/auth/login', {
    email: credentials.username, // Backend expects email field
    password: credentials.password
  });
  return response.data;
};

export const registerUser = async (userData: RegisterRequest): Promise<TokenResponse> => {
  const response = await apiClient.post('/api/auth/register', userData);
  return response.data;
};

export const refreshToken = async (token: string): Promise<TokenResponse> => {
  const response = await apiClient.post('/api/auth/refresh', {
    refresh_token: token
  });
  return response.data;
};

export const getUserProfile = async (): Promise<UserProfile> => {
  const response = await apiClient.get('/api/auth/profile');
  return response.data;
};

export const logoutUser = async (): Promise<{ success: boolean; message: string }> => {
  const response = await apiClient.post('/api/auth/logout');
  return response.data;
};

// === TOKEN MANAGEMENT ===

export const setAuthTokens = (tokenData: TokenResponse): void => {
  logger.log('Storing authentication tokens');
  localStorage.setItem('owen_access_token', tokenData.access_token);
  localStorage.setItem('owen_refresh_token', tokenData.refresh_token);
  localStorage.setItem('owen_token_type', tokenData.token_type);
  localStorage.setItem('owen_token_expires', (Date.now() + tokenData.expires_in * 1000).toString());
};

export const clearAuthTokens = (): void => {
  logger.log('Clearing all authentication tokens');
  const tokenKeys = [
    'owen_access_token',
    'owen_refresh_token',
    'owen_token_type',
    'owen_token_expires',
    // Legacy keys without prefix
    'access_token',
    'refresh_token',
    'token_type',
    'expires_at'
  ];
  tokenKeys.forEach(key => localStorage.removeItem(key));
};

export const getStoredTokens = (): {
  accessToken: string | null;
  refreshToken: string | null;
  tokenType: string | null;
  expiresAt: number | null;
} => {
  return {
    accessToken: localStorage.getItem('owen_access_token'),
    refreshToken: localStorage.getItem('owen_refresh_token'),
    tokenType: localStorage.getItem('owen_token_type'),
    expiresAt: localStorage.getItem('owen_token_expires')
      ? parseInt(localStorage.getItem('owen_token_expires')!)
      : null
  };
};

export const isTokenExpired = (): boolean => {
  const expiresAt = localStorage.getItem('owen_token_expires');
  if (!expiresAt) return true;

  const expirationTime = parseInt(expiresAt);
  return Date.now() >= expirationTime;
};
