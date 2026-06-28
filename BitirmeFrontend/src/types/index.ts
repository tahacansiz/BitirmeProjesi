/**
 * Central Type Exports
 * All types are exported from here for clean imports across the app
 */

export type { LoginCredentials, LoginResponse, AuthContextType, User, UserProfile } from './auth';
export type { Recipe, Ingredient, SavedRecipe, RecipeFilter } from './recipe';
export type { MealSuggestion, MealPlan } from './meal';

/**
 * API Response Types (Generic, backend-ready)
 */
export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: {
    code: string;
    message: string;
  };
  timestamp?: string;
}

export interface PaginatedResponse<T> {
  data: T[];
  total: number;
  page: number;
  pageSize: number;
  hasMore: boolean;
}
