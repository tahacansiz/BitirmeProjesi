"""Meal / weekly-plan routes."""
from __future__ import annotations

import ast
import json
import re
from typing import Optional

from fastapi import APIRouter, Body, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session


# ---------------------------------------------------------------------------
# Parsing helpers for tarifler.ingredients / tarifler.instructions
# ---------------------------------------------------------------------------

def _parse_ingredients(raw: Optional[str]) -> list[str]:
    """Convert raw ingredients field to a list of human-readable strings.

    Handles two observed formats:
    - JSON array:  [{"amount": "2 yemek kaşığı", "name": "un"}, ...]
    - Plain text:  "2 yemek kaşığı un\n1 adet yumurta"
    """
    if not raw:
        return []
    raw = raw.strip()
    # Try JSON first
    if raw.startswith("["):
        try:
            items = json.loads(raw)
            result = []
            for item in items:
                if isinstance(item, dict):
                    amount = (item.get("amount") or "").strip()
                    name = (item.get("name") or "").strip()
                    line = f"{amount} {name}".strip() if amount else name
                    if line:
                        result.append(line)
                elif isinstance(item, str) and item.strip():
                    result.append(item.strip())
            return result
        except (json.JSONDecodeError, TypeError, ValueError):
            pass
    # Fallback: split by newline or comma
    lines = [l.strip() for l in re.split(r"[\n,]", raw) if l.strip()]
    return lines


def _parse_instructions(raw: Optional[str]) -> list[str]:
    """Convert raw instructions field to an ordered list of step strings.

    Observed format:  "1. ['adım1', 'adım2', ...]"
    Also handles plain numbered text or newline-separated text.
    """
    if not raw:
        return []
    raw = raw.strip()

    # Format: "1. ['step1', 'step2', ...]"  — strip leading "1. " then eval the list
    m = re.match(r"^\d+\.\s*(\[.+)", raw, re.DOTALL)
    if m:
        list_str = m.group(1).strip()
        try:
            items = ast.literal_eval(list_str)
            if isinstance(items, list):
                return [str(s).strip() for s in items if str(s).strip()]
        except (ValueError, SyntaxError):
            pass

    # Plain JSON array
    if raw.startswith("["):
        try:
            items = json.loads(raw)
            if isinstance(items, list):
                return [str(s).strip() for s in items if str(s).strip()]
        except (json.JSONDecodeError, ValueError):
            pass

    # Numbered lines: "1. step\n2. step"
    lines = re.split(r"\n+", raw)
    cleaned = []
    for line in lines:
        line = re.sub(r"^\d+[\.\)]\s*", "", line).strip()
        if line:
            cleaned.append(line)
    return cleaned

from app.core.database import get_db
from app.deps import get_current_user
from app.models.meal_plan import MealPlan
from app.models.recipe import Recipe
from app.models.tarif import Tarif
from app.models.user import User
from app.schemas.meal import (
    MealOut,
    RecipeDetailOut,
    SaveMealPlanRequest,
    WeeklyMealPlanOut,
)
from app.services import ai_planner

router = APIRouter(prefix="/meals", tags=["meals"])


@router.get("/weekly-plan", response_model=WeeklyMealPlanOut)
def get_weekly_plan(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    week_start: Optional[str] = Query(default=None, description="ISO date (YYYY-MM-DD)"),
    health_condition: Optional[str] = Query(default=None),
) -> WeeklyMealPlanOut:
    """Generate the personalised 7-day plan for the current user."""
    return ai_planner.generate_weekly_plan(
        db, current_user, week_start=week_start, health_condition=health_condition
    )


@router.post("/suggest", response_model=WeeklyMealPlanOut)
def suggest_plan(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    week_start: Optional[str] = Body(default=None, embed=True),
    health_condition: Optional[str] = Body(default=None, embed=True),
) -> WeeklyMealPlanOut:
    """Request a fresh AI suggestion (same generator as the weekly plan)."""
    return ai_planner.generate_weekly_plan(
        db, current_user, week_start=week_start, health_condition=health_condition
    )


@router.get("/alternatives", response_model=list[MealOut])
def alternatives(
    category: str = Query(..., description="breakfast|main|side|snack"),
    exclude_meal_id: Optional[str] = Query(default=None),
    db: Session = Depends(get_db),
) -> list[MealOut]:
    """Return alternative meals that can replace a meal of the given category."""
    return ai_planner.get_alternatives(db, category, exclude_meal_id)


@router.post("/plan", status_code=201)
def save_plan(
    payload: SaveMealPlanRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    """Persist a generated weekly plan for the current user."""
    meal_plan = MealPlan(
        user_id=current_user.id, week_start=payload.weekStart, plan=payload.plan
    )
    db.add(meal_plan)
    db.commit()
    db.refresh(meal_plan)
    return {"success": True, "id": meal_plan.id}


@router.get("/plan")
def get_saved_plan(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    week_start: Optional[str] = Query(default=None),
) -> dict:
    """Return the latest saved plan for the user (optionally for a given week)."""
    stmt = select(MealPlan).where(MealPlan.user_id == current_user.id)
    if week_start:
        stmt = stmt.where(MealPlan.week_start == week_start)
    stmt = stmt.order_by(MealPlan.created_at.desc())
    plan = db.execute(stmt).scalars().first()
    if plan is None:
        return {"success": True, "plan": None}
    return {"success": True, "id": plan.id, "weekStart": plan.week_start, "plan": plan.plan}


@router.get("/recipe/{recipe_id}", response_model=RecipeDetailOut)
def get_recipe_detail(
    recipe_id: str,
    db: Session = Depends(get_db),
) -> RecipeDetailOut:
    """Return full recipe detail by joining recipes + tarifler."""
    tarif = db.get(Tarif, recipe_id)
    recipe = db.get(Recipe, recipe_id)
    if tarif is None and recipe is None:
        raise HTTPException(status_code=404, detail="Recipe not found.")

    raw_title = tarif.title if tarif else None
    clean = raw_title.strip().removesuffix("Tarifi").strip() if raw_title else recipe_id

    return RecipeDetailOut(
        id=recipe_id,
        title=clean,
        ingredients=_parse_ingredients(tarif.ingredients if tarif else None),
        instructions=_parse_instructions(tarif.instructions if tarif else None),
        prepTimeMin=tarif.prep_time_min if tarif else None,
        cookTimeMin=tarif.cook_time_min if tarif else None,
        servings=tarif.servings if tarif else None,
        calories=round(float(recipe.calories_pp or 0), 1) if recipe else 0,
        protein=round(float(recipe.protein_g_pp or 0), 1) if recipe else 0,
        carbs=round(float(recipe.carbs_g_pp or 0), 1) if recipe else 0,
        fat=round(float(recipe.fat_g_pp or 0), 1) if recipe else 0,
    )
