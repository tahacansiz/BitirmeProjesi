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

  if (!isAuthenticated && !authLoading) return <Navigate to="/login" replace />;
  if (needsOnboarding && !authLoading) return <Navigate to="/onboarding" replace />;

  return (
    <div className="saved-recipes-page">
      <div className="saved-recipes-page__container">
        <section className="saved-recipes-page__header">
          <h1 className="saved-recipes-page__title">Kaydedilen Tarifler</h1>
          <p className="saved-recipes-page__subtitle">
            {savedRecipes.length} tarif kaydedildi
          </p>
        </section>

        {isLoading ? (
          <LoadingSpinner message="Kaydedilen tarifler yükleniyor..." />
        ) : (
          <RecipeGrid
            recipes={savedRecipes}
            savedRecipeIds={savedRecipes.map((r) => r.id)}
            onRemove={removeSavedRecipe}
            emptyMessage="Henüz kaydedilen tarif yok. Tarif kütüphanesini keşfedin!"
          />
        )}
      </div>
    </div>
  );
};
