/**
 * Authentication Types
 * Backend-ready: These types will match API responses later
 */

export interface LoginCredentials {
  email: string;
  password: string;
}

export interface LoginResponse {
  success: boolean;
  token?: string;
  user?: User;
  message?: string;
}

export interface AuthContextType {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (credentials: LoginCredentials) => Promise<void>;
  logout: () => void;
  clearError: () => void;
  refreshUser: () => void;
  error: string | null;
}

export interface User {
  id: string;
  email: string;
  firstName?: string;
  lastName?: string;
  isOnboarded: boolean;
  profile?: UserProfile;
}

export interface UserProfile {
  age: number;
  height: number; // in cm
  weight: number; // in kg
  gender: 'male' | 'female' | 'other';
  activityLevel: 'low' | 'medium' | 'high';
  healthCondition: string;
  createdAt?: string;
  updatedAt?: string;
}
