"""Saved (favourite) recipe routes."""
from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Body, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.deps import get_current_user
from app.models.recipe import Recipe
from app.models.saved_recipe import SavedRecipe
from app.models.user import User
from app.schemas.recipe import RecipeOut

router = APIRouter(prefix="/saved-recipes", tags=["saved-recipes"])


def _saved_recipe_ids(db: Session, user_id: int) -> list[int]:
    stmt = select(SavedRecipe.recipe_id).where(SavedRecipe.user_id == user_id)
    return list(db.execute(stmt).scalars())


@router.get("", response_model=list[RecipeOut])
def list_saved_recipes(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
) -> list[Recipe]:
    ids = _saved_recipe_ids(db, current_user.id)
    if not ids:
        return []
    stmt = select(Recipe).where(Recipe.recipe_id.in_(ids))
    return list(db.execute(stmt).scalars())


# Alias kept for frontend compatibility (SAVED_RECIPES.GET_USER_SAVED).
@router.get("/user", response_model=list[RecipeOut])
def list_current_user_saved(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
) -> list[Recipe]:
    return list_saved_recipes(current_user, db)


@router.post("", status_code=status.HTTP_201_CREATED)
def save_recipe(
    recipe_id: int = Body(..., embed=True),
    notes: Optional[str] = Body(default=None, embed=True),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    if db.get(Recipe, recipe_id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recipe not found.")

    existing = db.execute(
        select(SavedRecipe).where(
            SavedRecipe.user_id == current_user.id, SavedRecipe.recipe_id == recipe_id
        )
    ).scalar_one_or_none()
    if existing is None:
        db.add(SavedRecipe(user_id=current_user.id, recipe_id=recipe_id, notes=notes))
        db.commit()
    return {"success": True}


@router.delete("/{recipe_id}", status_code=status.HTTP_200_OK)
def remove_saved_recipe(
    recipe_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> None:
    saved = db.execute(
        select(SavedRecipe).where(
            SavedRecipe.user_id == current_user.id, SavedRecipe.recipe_id == recipe_id
        )
    ).scalar_one_or_none()
    if saved is not None:
        db.delete(saved)
        db.commit()
