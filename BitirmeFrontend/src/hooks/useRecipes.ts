/**
 * Recipe Hooks
 * Handle recipe fetching and management
 */

import { useState, useCallback, useEffect } from 'react';
import type { Recipe, SavedRecipe } from '../types/recipe';
import { recipeService } from '../services/recipe/recipeService';

export const useRecipes = () => {
  const [recipes, setRecipes] = useState<Recipe[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchRecipes = useCallback(async () => {
    setIsLoading(true);
    setError(null);

    try {
      const data = await recipeService.getRecipes();
      setRecipes(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch recipes');
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchRecipes();
  }, [fetchRecipes]);

  return { recipes, isLoading, error, refetch: fetchRecipes };
};

/**
 * useSavedRecipes Hook
 */
export const useSavedRecipes = () => {
  const [savedRecipes, setSavedRecipes] = useState<SavedRecipe[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchSavedRecipes = useCallback(async () => {
    setIsLoading(true);
    setError(null);

    try {
      const data = await recipeService.getSavedRecipes();
      setSavedRecipes(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch saved recipes');
    } finally {
      setIsLoading(false);
    }
  }, []);

  const saveRecipe = useCallback(
    async (recipeId: string) => {
      try {
        await recipeService.saveRecipe(recipeId);
        await fetchSavedRecipes(); // Refresh list
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to save recipe');
      }
    },
    [fetchSavedRecipes]
  );

  const removeSavedRecipe = useCallback(
    async (recipeId: string) => {
      try {
        await recipeService.removeSavedRecipe(recipeId);
        setSavedRecipes((prev) => prev.filter((r) => r.id !== recipeId));
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to remove recipe');
      }
    },
    []
  );

  useEffect(() => {
    fetchSavedRecipes();
  }, [fetchSavedRecipes]);

  return {
    savedRecipes,
    isLoading,
    error,
    saveRecipe,
    removeSavedRecipe,
    refetch: fetchSavedRecipes,
  };
};
