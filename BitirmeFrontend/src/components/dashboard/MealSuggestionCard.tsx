/**
 * MealSuggestionCard Component
 * Displays meal suggestions from AI recommendations
 */

import React from 'react';
import type { MealSuggestion } from '../../types/meal';
import { Button } from '../common/Button';
import '../../styles/components.css';

interface MealSuggestionCardProps {
  suggestion: MealSuggestion;
  onSelect?: () => void;
}

export const MealSuggestionCard: React.FC<MealSuggestionCardProps> = ({
  suggestion,
  onSelect,
}) => {
  return (
    <div className="meal-suggestion-card">
      <img
        src={suggestion.recipe.image}
        alt={suggestion.recipe.title}
        className="meal-suggestion-card__image"
      />
      <div className="meal-suggestion-card__content">
        <h4 className="meal-suggestion-card__title">
          {suggestion.recipe.title}
        </h4>
        {suggestion.reason && (
          <p className="meal-suggestion-card__reason">💡 {suggestion.reason}</p>
        )}
        <div className="meal-suggestion-card__nutrition">
          <span className="meal-suggestion-card__cal">
            {suggestion.recipe.calories} cal
          </span>
          <span className="meal-suggestion-card__protein">
            {suggestion.recipe.protein}g protein
          </span>
        </div>
        {onSelect && (
          <Button onClick={onSelect} variant="primary" size="small" fullWidth>
            View Recipe
          </Button>
        )}
      </div>
    </div>
  );
};
