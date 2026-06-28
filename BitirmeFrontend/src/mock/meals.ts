/**
 * Mock Meal Suggestions
 * Simulates AI-generated recommendations from backend
 */

import type { MealSuggestion } from '../types/meal';

export const mockMealSuggestions: MealSuggestion[] = [
  {
    id: 'suggestion-1',
    recipe: {
      id: '1',
      title: 'Grilled Chicken with Quinoa',
      image: 'https://images.unsplash.com/photo-1598103442097-8b74394b95c6?w=400&h=300&fit=crop',
      calories: 450,
      protein: 45,
      carbs: 35,
      fat: 12,
    },
    reason: 'High protein, matches your fitness goals',
  },
  {
    id: 'suggestion-2',
    recipe: {
      id: '2',
      title: 'Salmon Buddha Bowl',
      image: 'https://images.unsplash.com/photo-1546069901-ba9599a7e63c?w=400&h=300&fit=crop',
      calories: 520,
      protein: 38,
      carbs: 52,
      fat: 18,
    },
    reason: 'Rich in omega-3, supports heart health',
  },
  {
    id: 'suggestion-3',
    recipe: {
      id: '4',
      title: 'Protein Smoothie Bowl',
      image: 'https://images.unsplash.com/photo-1590080876614-be9c29b29330?w=400&h=300&fit=crop',
      calories: 380,
      protein: 28,
      carbs: 52,
      fat: 8,
    },
    reason: 'Quick breakfast option, high in protein',
  },
];
