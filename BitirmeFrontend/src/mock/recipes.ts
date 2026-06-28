/**
 * Mock Recipe Data
 * Structure is production-ready and matches API format
 * Replace these with actual API calls later
 */

import type { Recipe } from '../types/recipe';

export const mockRecipes: Recipe[] = [
  {
    id: '1',
    title: 'Grilled Chicken with Quinoa',
    description: 'Healthy grilled chicken breast served with nutritious quinoa and steamed vegetables.',
    image: 'https://images.unsplash.com/photo-1598103442097-8b74394b95c6?w=400&h=300&fit=crop',
    calories: 450,
    protein: 45,
    carbs: 35,
    fat: 12,
    servings: 2,
    prepTime: 15,
    cookTime: 20,
    difficulty: 'easy',
    tags: ['high-protein', 'low-fat', 'gluten-free'],
    ingredients: [
      { id: '1-1', name: 'Chicken Breast', amount: 200, unit: 'g', calories: 165, protein: 31, carbs: 0, fat: 3.6 },
      { id: '1-2', name: 'Quinoa', amount: 1, unit: 'cup', calories: 222, protein: 8, carbs: 39, fat: 4 },
      { id: '1-3', name: 'Broccoli', amount: 150, unit: 'g', calories: 55, protein: 3.7, carbs: 11, fat: 0.4 },
    ],
    instructions: [
      'Season chicken with salt, pepper, and herbs',
      'Grill chicken for 8-10 minutes per side',
      'Cook quinoa according to package directions',
      'Steam broccoli until tender-crisp',
      'Plate and serve hot',
    ],
  },
  {
    id: '2',
    title: 'Salmon Buddha Bowl',
    description: 'Omega-3 rich salmon with brown rice, vegetables, and tahini dressing.',
    image: 'https://images.unsplash.com/photo-1546069901-ba9599a7e63c?w=400&h=300&fit=crop',
    calories: 520,
    protein: 38,
    carbs: 52,
    fat: 18,
    servings: 1,
    prepTime: 10,
    cookTime: 15,
    difficulty: 'easy',
    tags: ['high-protein', 'omega-3', 'heart-healthy'],
    ingredients: [
      { id: '2-1', name: 'Salmon Fillet', amount: 150, unit: 'g', calories: 280, protein: 25, carbs: 0, fat: 17 },
      { id: '2-2', name: 'Brown Rice', amount: 150, unit: 'g', calories: 195, protein: 5, carbs: 43, fat: 2 },
      { id: '2-3', name: 'Avocado', amount: 0.5, unit: 'piece', calories: 120, protein: 1.5, carbs: 6, fat: 11 },
    ],
    instructions: [
      'Bake salmon at 200°C for 12-15 minutes',
      'Cook brown rice according to package directions',
      'Arrange rice in a bowl',
      'Add salmon and fresh vegetables',
      'Drizzle with tahini dressing',
    ],
  },
  {
    id: '3',
    title: 'Greek Salad with Feta',
    description: 'Fresh vegetables with feta cheese, olives, and olive oil dressing.',
    image: 'https://images.unsplash.com/photo-1540189549336-e6e99c3679fe?w=400&h=300&fit=crop',
    calories: 280,
    protein: 12,
    carbs: 15,
    fat: 20,
    servings: 1,
    prepTime: 10,
    cookTime: 0,
    difficulty: 'easy',
    tags: ['vegetarian', 'low-carb', 'mediterranean'],
    ingredients: [
      { id: '3-1', name: 'Tomato', amount: 2, unit: 'pieces', calories: 33, protein: 1.5, carbs: 7, fat: 0.2 },
      { id: '3-2', name: 'Cucumber', amount: 1, unit: 'piece', calories: 45, protein: 2, carbs: 10, fat: 0.2 },
      { id: '3-3', name: 'Feta Cheese', amount: 100, unit: 'g', calories: 264, protein: 14, carbs: 4, fat: 21 },
    ],
    instructions: [
      'Chop all vegetables into bite-sized pieces',
      'Add olives and feta cheese',
      'Drizzle with olive oil and lemon juice',
      'Season with salt and oregano',
      'Toss and serve',
    ],
  },
  {
    id: '4',
    title: 'Protein Smoothie Bowl',
    description: 'Creamy smoothie bowl with berries, granola, and chia seeds.',
    image: 'https://images.unsplash.com/photo-1590080876614-be9c29b29330?w=400&h=300&fit=crop',
    calories: 380,
    protein: 28,
    carbs: 52,
    fat: 8,
    servings: 1,
    prepTime: 5,
    cookTime: 0,
    difficulty: 'easy',
    tags: ['quick', 'high-protein', 'vegetarian'],
    ingredients: [
      { id: '4-1', name: 'Greek Yogurt', amount: 200, unit: 'g', calories: 130, protein: 20, carbs: 9, fat: 0 },
      { id: '4-2', name: 'Berries', amount: 150, unit: 'g', calories: 80, protein: 1, carbs: 19, fat: 0.3 },
      { id: '4-3', name: 'Granola', amount: 40, unit: 'g', calories: 170, protein: 4, carbs: 28, fat: 6 },
    ],
    instructions: [
      'Blend yogurt with berries until smooth',
      'Pour into a bowl',
      'Top with granola and chia seeds',
      'Add fresh fruit',
      'Serve immediately',
    ],
  },
  {
    id: '5',
    title: 'Turkey Meatballs with Pasta',
    description: 'Lean ground turkey meatballs served with whole wheat pasta and marinara sauce.',
    image: 'https://images.unsplash.com/photo-1621996346565-e3dbc646d9a9?w=400&h=300&fit=crop',
    calories: 420,
    protein: 42,
    carbs: 48,
    fat: 9,
    servings: 2,
    prepTime: 20,
    cookTime: 25,
    difficulty: 'medium',
    tags: ['high-protein', 'whole-grain'],
    ingredients: [
      { id: '5-1', name: 'Ground Turkey', amount: 300, unit: 'g', calories: 320, protein: 35, carbs: 0, fat: 18 },
      { id: '5-2', name: 'Whole Wheat Pasta', amount: 200, unit: 'g', calories: 200, protein: 8, carbs: 43, fat: 1 },
      { id: '5-3', name: 'Marinara Sauce', amount: 150, unit: 'ml', calories: 60, protein: 2, carbs: 10, fat: 1 },
    ],
    instructions: [
      'Mix ground turkey with breadcrumbs and herbs',
      'Form into balls and bake at 200°C for 20 minutes',
      'Cook pasta according to package directions',
      'Warm marinara sauce in a pan',
      'Combine pasta, sauce, and meatballs',
    ],
  },
];

export const mockSavedRecipes: Recipe[] = [
  mockRecipes[0], // Grilled Chicken
  mockRecipes[1], // Salmon Bowl
];
