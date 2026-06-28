/**
 * Saved Recipes Page
 * Display user's saved/bookmarked recipes
 */

import React from 'react';
import { Navigate } from 'react-router-dom';
import { useAuthStatus, useOnboarding } from '../hooks/useAuth';
import { useSavedRecipes } from '../hooks/useRecipes';
import { LoadingSpinner } from '../components/common/LoadingSpinner';
import { RecipeGrid } from '../components/recipe/RecipeGrid';
import '../styles/pages.css';

export const SavedRecipesPage: React.FC = () => {
  const { isAuthenticated, isLoading: authLoading } = useAuthStatus();
  const { needsOnboarding } = useOnboarding();
  const { savedRecipes, isLoading, removeSavedRecipe } = useSavedRecipes();

  // Redirect if not authenticated
  if (!isAuthenticated && !authLoading) {
    return <Navigate to="/login" replace />;
  }

  // Redirect if onboarding not completed
  if (needsOnboarding && !authLoading) {
    return <Navigate to="/onboarding" replace />;
  }

  return (
    <div className="saved-recipes-page">
      <div className="saved-recipes-page__container">
        <section className="saved-recipes-page__header">
          <h1 className="saved-recipes-page__title">Saved Recipes</h1>
          <p className="saved-recipes-page__subtitle">
            {savedRecipes.length} recipe
            {savedRecipes.length !== 1 ? 's' : ''} saved
          </p>
        </section>

        {isLoading ? (
          <LoadingSpinner message="Loading saved recipes..." />
        ) : (
          <RecipeGrid
            recipes={savedRecipes}
            savedRecipeIds={savedRecipes.map((r) => r.id)}
            onRemove={removeSavedRecipe}
            emptyMessage="You haven't saved any recipes yet. Visit the recipe library to get started!"
          />
        )}
      </div>
    </div>
  );
};
