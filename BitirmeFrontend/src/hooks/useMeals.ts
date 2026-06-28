/**
 * Meal Hooks
 * Handle meal suggestions and meal planning
 */

import { useState, useCallback, useEffect } from 'react';
import type { MealSuggestion, MealPlan } from '../types/meal';
import { mealService } from '../services/recipe/mealService';

export const useMealSuggestions = () => {
  const [suggestions, setSuggestions] = useState<MealSuggestion[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchSuggestions = useCallback(async () => {
    setIsLoading(true);
    setError(null);

    try {
      const data = await mealService.getMealSuggestions();
      setSuggestions(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch suggestions');
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchSuggestions();
  }, [fetchSuggestions]);

  return {
    suggestions,
    isLoading,
    error,
    refetch: fetchSuggestions,
  };
};

/**
 * useMealPlan Hook
 */
export const useMealPlan = (date: string) => {
  const [mealPlan, setMealPlan] = useState<MealPlan | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchMealPlan = useCallback(async () => {
    setIsLoading(true);
    setError(null);

    try {
      const data = await mealService.getMealPlan(date);
      setMealPlan(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch meal plan');
    } finally {
      setIsLoading(false);
    }
  }, [date]);

  useEffect(() => {
    if (date) {
      fetchMealPlan();
    }
  }, [date, fetchMealPlan]);

  return {
    mealPlan,
    isLoading,
    error,
    refetch: fetchMealPlan,
  };
};
