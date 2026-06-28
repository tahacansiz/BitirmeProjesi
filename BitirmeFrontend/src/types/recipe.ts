/**
 * Recipe Types
 * Backend-ready: Will connect to recipe service API
 */

export interface Recipe {
  id: string;
  title: string;
  description?: string;
  image: string;
  calories: number;
  protein: number;
  carbs: number;
  fat: number;
  servings?: number;
  prepTime?: number; // in minutes
  cookTime?: number; // in minutes
  difficulty?: 'easy' | 'medium' | 'hard';
  ingredients?: Ingredient[];
  instructions?: string[];
  tags?: string[];
  createdAt?: string;
}

export interface Ingredient {
  id: string;
  name: string;
  amount: number;
  unit: string;
  calories?: number;
  protein?: number;
  carbs?: number;
  fat?: number;
}

export interface SavedRecipe extends Recipe {
  savedAt: string;
  userId?: string;
  notes?: string;
}

export interface RecipeFilter {
  minCalories?: number;
  maxCalories?: number;
  difficulty?: 'easy' | 'medium' | 'hard';
  tags?: string[];
  searchQuery?: string;
}
