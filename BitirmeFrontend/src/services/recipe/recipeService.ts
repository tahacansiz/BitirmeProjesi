/**
 * Recipe Service
 * Handles recipe fetching, searching, and management
 * Currently uses mock data, ready for API integration
 */

import type { Recipe, SavedRecipe } from '../../types/recipe';
import { mockRecipes, mockSavedRecipes } from '../../mock/recipes';

const API_DELAY = 300;

class RecipeService {
  /**
   * Get all recipes
   * @returns Array of recipes
   */
  async getRecipes(): Promise<Recipe[]> {
    // TODO: Replace with API call
    // const response = await apiClient.get<Recipe[]>('/recipes');
    // return response.data || [];

    // MOCK IMPLEMENTATION
    await new Promise((resolve) => setTimeout(resolve, API_DELAY));
    return mockRecipes;
  }

  /**
   * Get recipe by ID
   * @param id Recipe ID
   */
  async getRecipeById(id: string): Promise<Recipe | null> {
    // TODO: Replace with API call
    // const response = await apiClient.get<Recipe>(`/recipes/${id}`);

    // MOCK IMPLEMENTATION
    await new Promise((resolve) => setTimeout(resolve, API_DELAY));
    return mockRecipes.find((r) => r.id === id) || null;
  }

  /**
   * Search recipes
   * @param query Search query
   */
  async searchRecipes(query: string): Promise<Recipe[]> {
    // TODO: Replace with API call
    // const response = await apiClient.get<Recipe[]>(`/recipes/search?q=${query}`);

    // MOCK IMPLEMENTATION
    await new Promise((resolve) => setTimeout(resolve, API_DELAY));

    return mockRecipes.filter(
      (r) =>
        r.title.toLowerCase().includes(query.toLowerCase()) ||
        r.description?.toLowerCase().includes(query.toLowerCase())
    );
  }

  /**
   * Filter recipes by calories and difficulty
   */
  async filterRecipes(
    minCalories?: number,
    maxCalories?: number,
    difficulty?: string
  ): Promise<Recipe[]> {
    // TODO: Replace with API call

    // MOCK IMPLEMENTATION
    await new Promise((resolve) => setTimeout(resolve, API_DELAY));

    return mockRecipes.filter((r) => {
      if (minCalories && r.calories < minCalories) return false;
      if (maxCalories && r.calories > maxCalories) return false;
      if (difficulty && r.difficulty !== difficulty) return false;
      return true;
    });
  }

  /**
   * Get saved recipes for current user
   */
  async getSavedRecipes(): Promise<SavedRecipe[]> {
    // TODO: Replace with API call
    // const response = await apiClient.get<SavedRecipe[]>('/saved-recipes');

    // MOCK IMPLEMENTATION
    await new Promise((resolve) => setTimeout(resolve, API_DELAY));
    return mockSavedRecipes as SavedRecipe[];
  }

  /**
   * Save recipe for user
   * @param recipeId ID of recipe to save
   */
  async saveRecipe(recipeId: string): Promise<boolean> {
    // TODO: Replace with API call
    // const response = await apiClient.post('/saved-recipes', { recipeId });

    // MOCK IMPLEMENTATION
    await new Promise((resolve) => setTimeout(resolve, API_DELAY));

    const recipe = mockRecipes.find((r) => r.id === recipeId);
    if (!recipe) return false;

    // Add to saved recipes if not already there
    if (!mockSavedRecipes.find((r) => r.id === recipeId)) {
      mockSavedRecipes.push(recipe as SavedRecipe);
    }

    return true;
  }

  /**
   * Remove saved recipe
   * @param recipeId ID of recipe to remove
   */
  async removeSavedRecipe(recipeId: string): Promise<boolean> {
    // TODO: Replace with API call
    // const response = await apiClient.delete(`/saved-recipes/${recipeId}`);

    // MOCK IMPLEMENTATION
    await new Promise((resolve) => setTimeout(resolve, API_DELAY));

    const index = mockSavedRecipes.findIndex((r) => r.id === recipeId);
    if (index > -1) {
      mockSavedRecipes.splice(index, 1);
      return true;
    }

    return false;
  }
}

export const recipeService = new RecipeService();
