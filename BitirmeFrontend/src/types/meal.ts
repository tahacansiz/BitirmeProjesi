/**
 * Meal Suggestion Types
 * Backend-ready: AI-based recommendations will come from backend
 */

export interface MealSuggestion {
  id: string;
  recipe: {
    id: string;
    title: string;
    image: string;
    calories: number;
    protein: number;
    carbs: number;
    fat: number;
  };
  reason?: string; // e.g., "Matches your calorie goal"
  suggestedAt?: string;
}

export interface MealPlan {
  id: string;
  userId?: string;
  date: string;
  meals: {
    breakfast?: MealSuggestion;
    lunch?: MealSuggestion;
    dinner?: MealSuggestion;
    snack?: MealSuggestion;
  };
  totalCalories?: number;
  totalProtein?: number;
  totalCarbs?: number;
  totalFat?: number;
}
