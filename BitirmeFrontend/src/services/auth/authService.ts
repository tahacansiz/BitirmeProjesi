/**
 * Authentication Service
 * Handles login, logout, and authentication state via the real backend.
 */

import type { LoginCredentials, LoginResponse, User } from '../../types/auth';
import { apiClient } from '../api/client';

class AuthService {
  async login(credentials: LoginCredentials): Promise<LoginResponse> {
    const response = await apiClient.post<{ token: string; user: User }>(
      '/auth/login',
      credentials
    );

    if (response.success && response.data) {
      localStorage.setItem('auth_token', response.data.token);
      localStorage.setItem('user', JSON.stringify(response.data.user));
      return { success: true, user: response.data.user, token: response.data.token };
    }

    return { success: false, message: response.error?.message || 'Login failed' };
  }

  logout(): void {
    localStorage.removeItem('auth_token');
    localStorage.removeItem('user');
  }

  getCurrentUser(): User | null {
    const userStr = localStorage.getItem('user');
    if (!userStr) return null;
    try {
      return JSON.parse(userStr) as User;
    } catch {
      return null;
    }
  }

  isAuthenticated(): boolean {
    return !!localStorage.getItem('auth_token');
  }

  isOnboarded(): boolean {
    const user = this.getCurrentUser();
    return user?.isOnboarded ?? false;
  }

  async completeOnboarding(userData: any): Promise<boolean> {
    const response = await apiClient.post('/users/onboarding/complete', userData);
    if (response.success) {
      const user = this.getCurrentUser();
      if (user) {
        user.isOnboarded = true;
        user.profile = userData;
        localStorage.setItem('user', JSON.stringify(user));
      }
      return true;
    }
    return false;
  }

  async updateProfile(updates: any): Promise<boolean> {
    const response = await apiClient.put('/users/profile', updates);
    if (response.success) {
      const user = this.getCurrentUser();
      if (user) {
        user.profile = { ...(user.profile || {}), ...updates };
        localStorage.setItem('user', JSON.stringify(user));
      }
      return true;
    }
    return false;
  }
}

export const authService = new AuthService();
