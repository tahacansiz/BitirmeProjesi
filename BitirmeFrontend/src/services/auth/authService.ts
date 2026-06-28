/**
 * Authentication Service
 * Handles login, logout, and authentication state
 * Currently uses mock data, ready for API integration
 */

import type { LoginCredentials, LoginResponse, User } from '../../types/auth';
import { mockAuthResponse } from '../../mock/users';

/**
 * Mock delay to simulate API latency
 * Remove when connecting to real backend
 */
const API_DELAY = 500;

class AuthService {
  /**
   * Login user with email and password
   * @param credentials Email and password
   * @returns User data and success status
   */
  async login(credentials: LoginCredentials): Promise<LoginResponse> {
    // TODO: Replace with actual API call
    // const response = await apiClient.post<LoginResponse>('/auth/login', credentials);

    // MOCK IMPLEMENTATION
    await new Promise((resolve) => setTimeout(resolve, API_DELAY));

    const result = await mockAuthResponse(credentials.email, credentials.password);

    if (result.success && result.user) {
      // Simulate token storage
      localStorage.setItem('auth_token', 'mock-jwt-token-' + Date.now());
      localStorage.setItem('user', JSON.stringify(result.user));

      return {
        success: true,
        user: result.user,
        token: 'mock-jwt-token',
      };
    }

    return {
      success: false,
      message: result.error || 'Login failed',
    };
  }

  /**
   * Logout current user
   */
  logout(): void {
    localStorage.removeItem('auth_token');
    localStorage.removeItem('user');
  }

  /**
   * Get current logged-in user
   * @returns User object or null
   */
  getCurrentUser(): User | null {
    const userStr = localStorage.getItem('user');
    if (!userStr) return null;

    try {
      return JSON.parse(userStr) as User;
    } catch {
      return null;
    }
  }

  /**
   * Check if user is authenticated
   * @returns True if user is logged in
   */
  isAuthenticated(): boolean {
    return !!localStorage.getItem('auth_token');
  }

  /**
   * Check if user has completed onboarding
   * @returns True if user profile exists
   */
  isOnboarded(): boolean {
    const user = this.getCurrentUser();
    return user?.isOnboarded ?? false;
  }

  /**
   * Mark onboarding as complete
   * @param userData User profile data from onboarding
   */
  async completeOnboarding(userData: any): Promise<boolean> {
    // TODO: Replace with actual API call
    // const response = await apiClient.post('/users/onboarding/complete', userData);

    // MOCK IMPLEMENTATION
    await new Promise((resolve) => setTimeout(resolve, API_DELAY));

    const user = this.getCurrentUser();
    if (!user) return false;

    user.isOnboarded = true;
    user.profile = userData;

    localStorage.setItem('user', JSON.stringify(user));
    return true;
  }

  /**
   * Update user profile
   * @param updates Partial profile updates
   */
  async updateProfile(updates: any): Promise<boolean> {
    // TODO: Replace with actual API call

    // MOCK IMPLEMENTATION
    await new Promise((resolve) => setTimeout(resolve, API_DELAY));

    const user = this.getCurrentUser();
    if (!user) return false;

    user.profile = {
      ...(user.profile || {}),
      ...updates,
    };

    localStorage.setItem('user', JSON.stringify(user));
    return true;
  }
}

export const authService = new AuthService();
