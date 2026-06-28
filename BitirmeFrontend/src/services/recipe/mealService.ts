/**
 * Meal Suggestion Service
 * Handles meal recommendations and meal planning
 * AI recommendations will come from backend later
 */

import type { MealSuggestion, MealPlan } from '../../types/meal';
import { mockMealSuggestions } from '../../mock/meals';

const API_DELAY = 500;

class MealService {
  /**
   * Get meal suggestions based on user profile
   * @returns Array of meal suggestions
   */
  async getMealSuggestions(): Promise<MealSuggestion[]> {
    // TODO: Replace with AI-powered backend API call
    // const userProfile = await getUserProfile();
    // const response = await apiClient.post<MealSuggestion[]>('/meals/suggest', {
    //   userProfile,
    // });

    // MOCK IMPLEMENTATION
    await new Promise((resolve) => setTimeout(resolve, API_DELAY));
    return mockMealSuggestions;
  }

  /**
   * Get meal plan for a specific date
   * @param date ISO date string (YYYY-MM-DD)
   */
  async getMealPlan(date: string): Promise<MealPlan | null> {
    // TODO: Replace with API call

    // MOCK IMPLEMENTATION
    await new Promise((resolve) => setTimeout(resolve, API_DELAY));

    const suggestions = mockMealSuggestions;

    return {
      id: 'plan-' + date,
      date,
      meals: {
        breakfast: suggestions[2], // Smoothie bowl
        lunch: suggestions[0], // Grilled chicken
        dinner: suggestions[1], // Salmon bowl
      },
      totalCalories: 1350,
      totalProtein: 111,
      totalCarbs: 139,
      totalFat: 38,
    };
  }

  /**
   * Save meal plan (for later implementation)
   */
  async saveMealPlan(mealPlan: MealPlan): Promise<boolean> {
    // TODO: Replace with API call

    // MOCK IMPLEMENTATION
    await new Promise((resolve) => setTimeout(resolve, API_DELAY));
    return true;
  }

  /**
   * Get suggested recipes for a meal type
   */
  async suggestForMealType(mealType: 'breakfast' | 'lunch' | 'dinner' | 'snack'): Promise<MealSuggestion[]> {
    // TODO: Replace with AI backend

    // MOCK IMPLEMENTATION
    await new Promise((resolve) => setTimeout(resolve, API_DELAY));

    return mockMealSuggestions.slice(0, 2);
  }
}

export const mealService = new MealService();
