/**
 * RecipeGrid Component
 * Grid layout for displaying multiple recipes
 */

import React from 'react';
import type { Recipe } from '../../types/recipe';
import { RecipeCard } from './RecipeCard';
import '../../styles/components.css';

interface RecipeGridProps {
  recipes: Recipe[];
  savedRecipeIds?: string[];
  onSave?: (recipeId: string) => void;
  onRemove?: (recipeId: string) => void;
  onRecipeClick?: (recipe: Recipe) => void;
  emptyMessage?: string;
}

export const RecipeGrid: React.FC<RecipeGridProps> = ({
  recipes,
  savedRecipeIds = [],
  onSave,
  onRemove,
  onRecipeClick,
  emptyMessage = 'No recipes found',
}) => {
  if (recipes.length === 0) {
    return <div className="recipe-grid__empty">{emptyMessage}</div>;
  }

  return (
    <div className="recipe-grid">
      {recipes.map((recipe) => (
        <RecipeCard
          key={recipe.id}
          recipe={recipe}
          isSaved={savedRecipeIds.includes(recipe.id)}
          onSave={onSave}
          onRemove={onRemove}
          onClick={() => onRecipeClick?.(recipe)}
        />
      ))}
    </div>
  );
};
