/**
 * RecipeCard Component
 * Displays recipe information with save functionality
 */

import React, { useState } from 'react';
import type { Recipe } from '../../types/recipe';
import { Button } from '../common/Button';
import '../../styles/components.css';

interface RecipeCardProps {
  recipe: Recipe;
  isSaved?: boolean;
  onSave?: (recipeId: string) => void;
  onRemove?: (recipeId: string) => void;
  onClick?: () => void;
}

export const RecipeCard: React.FC<RecipeCardProps> = ({
  recipe,
  isSaved = false,
  onSave,
  onRemove,
  onClick,
}) => {
  const [isLoading, setIsLoading] = useState(false);

  const handleSaveClick = async (e: React.MouseEvent) => {
    e.stopPropagation();

    if (isSaved && onRemove) {
      setIsLoading(true);
      try {
        await onRemove(recipe.id);
      } finally {
        setIsLoading(false);
      }
    } else if (!isSaved && onSave) {
      setIsLoading(true);
      try {
        await onSave(recipe.id);
      } finally {
        setIsLoading(false);
      }
    }
  };

  return (
    <div className="recipe-card" onClick={onClick}>
      <div className="recipe-card__image-container">
        <img
          src={recipe.image}
          alt={recipe.title}
          className="recipe-card__image"
        />
        <div className="recipe-card__badge">
          {recipe.difficulty && (
            <span className="recipe-card__difficulty">
              {recipe.difficulty.charAt(0).toUpperCase() + recipe.difficulty.slice(1)}
            </span>
          )}
        </div>
      </div>

      <div className="recipe-card__content">
        <h3 className="recipe-card__title">{recipe.title}</h3>
        {recipe.description && (
          <p className="recipe-card__description">{recipe.description}</p>
        )}

        <div className="recipe-card__stats">
          <div className="recipe-card__stat">
            <span className="recipe-card__stat-label">Calories</span>
            <span className="recipe-card__stat-value">{recipe.calories}</span>
          </div>
          <div className="recipe-card__stat">
            <span className="recipe-card__stat-label">Protein</span>
            <span className="recipe-card__stat-value">{recipe.protein}g</span>
          </div>
          <div className="recipe-card__stat">
            <span className="recipe-card__stat-label">Carbs</span>
            <span className="recipe-card__stat-value">{recipe.carbs}g</span>
          </div>
          <div className="recipe-card__stat">
            <span className="recipe-card__stat-label">Fat</span>
            <span className="recipe-card__stat-value">{recipe.fat}g</span>
          </div>
        </div>

        {(onSave || onRemove) && (
          <Button
            onClick={handleSaveClick}
            isLoading={isLoading}
            variant={isSaved ? 'secondary' : 'primary'}
            size="small"
            fullWidth
          >
            {isSaved ? '✓ Saved' : '+ Save Recipe'}
          </Button>
        )}
      </div>
    </div>
  );
};
