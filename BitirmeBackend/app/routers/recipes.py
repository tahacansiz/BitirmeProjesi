"""Recipe CRUD + query routes (the AI candidate pool)."""
from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.recipe import Recipe
from app.schemas.recipe import RecipeCreate, RecipeOut, RecipeUpdate

router = APIRouter(prefix="/recipes", tags=["recipes"])

# Season query value -> column name.
_SEASON_COLUMNS = {
    "spring": "ilkbahar",
    "ilkbahar": "ilkbahar",
    "summer": "yaz",
    "yaz": "yaz",
    "autumn": "sonbahar",
    "fall": "sonbahar",
    "sonbahar": "sonbahar",
    "winter": "kis",
    "kis": "kis",
}


@router.get("", response_model=list[RecipeOut])
def list_recipes(
    db: Session = Depends(get_db),
    category: Optional[str] = Query(default=None),
    season: Optional[str] = Query(default=None, description="spring|summer|autumn|winter"),
    limit: int = Query(default=100, ge=1, le=1000),
    offset: int = Query(default=0, ge=0),
) -> list[Recipe]:
    stmt = select(Recipe)
    if category:
        stmt = stmt.where(Recipe.category == category)
    if season:
        col = _SEASON_COLUMNS.get(season.strip().lower())
        if col:
            stmt = stmt.where(getattr(Recipe, col) == 1)
    stmt = stmt.offset(offset).limit(limit)
    return list(db.execute(stmt).scalars())


@router.get("/search", response_model=list[RecipeOut])
def search_recipes(
    q: str = Query(..., min_length=1),
    db: Session = Depends(get_db),
    limit: int = Query(default=50, ge=1, le=500),
) -> list[Recipe]:
    stmt = (
        select(Recipe)
        .where(Recipe.category.ilike(f"%{q}%"))
        .limit(limit)
    )
    return list(db.execute(stmt).scalars())


@router.get("/{recipe_id}", response_model=RecipeOut)
def get_recipe(recipe_id: int, db: Session = Depends(get_db)) -> Recipe:
    recipe = db.get(Recipe, recipe_id)
    if recipe is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recipe not found.")
    return recipe


@router.post("", response_model=RecipeOut, status_code=status.HTTP_201_CREATED)
def create_recipe(payload: RecipeCreate, db: Session = Depends(get_db)) -> Recipe:
    data = payload.model_dump(exclude_unset=True)
    recipe = Recipe(**data)
    db.add(recipe)
    db.commit()
    db.refresh(recipe)
    return recipe


@router.put("/{recipe_id}", response_model=RecipeOut)
def update_recipe(recipe_id: int, payload: RecipeUpdate, db: Session = Depends(get_db)) -> Recipe:
    recipe = db.get(Recipe, recipe_id)
    if recipe is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recipe not found.")
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(recipe, key, value)
    db.commit()
    db.refresh(recipe)
    return recipe


@router.delete("/{recipe_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_recipe(recipe_id: int, db: Session = Depends(get_db)) -> None:
    recipe = db.get(Recipe, recipe_id)
    if recipe is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recipe not found.")
    db.delete(recipe)
    db.commit()
