/**
 * Custom Hooks
 * Provide easy access to Auth context and services
 */

import { useContext } from 'react';
import { AuthContext } from '../context/AuthContext';
import type { AuthContextType } from '../types/auth';

/**
 * useAuth Hook
 * Access authentication state and methods
 * @throws Error if used outside AuthProvider
 */
export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext);

  if (!context) {
    throw new Error('useAuth must be used within AuthProvider');
  }

  return context;
};

/**
 * useAuthStatus Hook
 * Simplified hook for just checking auth status
 */
export const useAuthStatus = () => {
  const { user, isAuthenticated, isLoading } = useAuth();

  return {
    user,
    isAuthenticated,
    isLoading,
  };
};

/**
 * useOnboarding Hook
 * Check and manage onboarding state
 */
export const useOnboarding = () => {
  const { user } = useAuth();

  const isOnboarded = user?.isOnboarded ?? false;
  const needsOnboarding = user && !isOnboarded;

  return {
    isOnboarded,
    needsOnboarding,
    userProfile: user?.profile,
  };
};
