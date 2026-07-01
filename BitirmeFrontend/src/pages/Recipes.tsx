import React, { useState } from 'react';
import { Navigate } from 'react-router-dom';
import { useAuthStatus, useOnboarding } from '../hooks/useAuth';
import { useRecipes, useSavedRecipes } from '../hooks/useRecipes';
import { LoadingSpinner } from '../components/common/LoadingSpinner';
import { RecipeGrid } from '../components/recipe/RecipeGrid';
import { Input } from '../components/common/Input';
import '../styles/pages.css';

export const RecipesPage: React.FC = () => {
  const { isAuthenticated, isLoading: authLoading } = useAuthStatus();
  const { needsOnboarding } = useOnboarding();
  const { recipes, isLoading: recipesLoading } = useRecipes();
  const { savedRecipes, saveRecipe, removeSavedRecipe } = useSavedRecipes();
  const [searchQuery, setSearchQuery] = useState('');

  if (!isAuthenticated && !authLoading) return <Navigate to="/login" replace />;
  if (needsOnboarding && !authLoading) return <Navigate to="/onboarding" replace />;

  const filteredRecipes = recipes.filter(
    (recipe) =>
      recipe.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      recipe.description?.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const savedRecipeIds = savedRecipes.map((r) => r.id);

  return (
    <div className="recipes-page">
      <div className="recipes-page__container">
        <section className="recipes-page__header">
          <h1 className="recipes-page__title">Tarif Kütüphanesi</h1>
          <p className="recipes-page__subtitle">
            {recipes.length} sağlıklı tarifi keşfedin
          </p>
        </section>

        <div className="recipes-page__search">
          <Input
            type="text"
            placeholder="Tarif ara..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
        </div>

        {recipesLoading ? (
          <LoadingSpinner message="Tarifler yükleniyor..." />
        ) : (
          <RecipeGrid
            recipes={filteredRecipes}
            savedRecipeIds={savedRecipeIds}
            onSave={saveRecipe}
            onRemove={removeSavedRecipe}
            emptyMessage={
              searchQuery
                ? `"${searchQuery}" için tarif bulunamadı`
                : 'Henüz tarif bulunmuyor'
            }
          />
        )}
      </div>
    </div>
  );
};
