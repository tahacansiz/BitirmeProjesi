"""Weekly meal-plan generation.

The real recommendation model is **not ready yet**. This module implements a
deterministic placeholder ("stub") that picks recipes from the ``recipes`` table
using the same signals the AI model will eventually use (season, budget, dietary
preference and health condition). When the model is ready, replace
:func:`generate_weekly_plan` with a call that sends ``build_model_payload`` to
the model service and maps its response back into :class:`WeeklyMealPlanOut`.
"""
from __future__ import annotations

import random
from datetime import date, datetime, timedelta
from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.recipe import Recipe
from app.models.user import User
from app.schemas.meal import (
    DayMealsOut,
    DayPlanOut,
    MealOut,
    WeeklyMealPlanOut,
)

DAY_NAMES = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

# Maps a frontend "healthCondition" label to the matching recipes column.
HEALTH_CONDITION_COLUMNS = {
    "diabetes": "diabetes",
    "celiac": "celiac",
    "lactose intolerance": "lactose_intolerance",
    "lactose": "lactose_intolerance",
    "hypertension": "hypertension",
    "pregnancy": "pregnancy",
    "obesity": "obesity",
    "cardiovascular disease": "cardiovascular_disease",
    "cardiovascular": "cardiovascular_disease",
    "kidney disease": "kidney_disease",
    "kidney": "kidney_disease",
    "liver disease": "liver_disease",
    "liver": "liver_disease",
    "anemia": "anemia",
}

# Budget tier -> upper bound on the normalised cost (maliyet_norm, assumed 0-1).
BUDGET_CEILINGS = {"low": 0.4, "medium": 0.7, "high": 1.01}


def _season_column_for(d: date) -> str:
    """Return the seasonal flag column name for the given date (Northern hemisphere)."""
    month = d.month
    if month in (3, 4, 5):
        return "ilkbahar"  # spring
    if month in (6, 7, 8):
        return "yaz"  # summer
    if month in (9, 10, 11):
        return "sonbahar"  # autumn
    return "kis"  # winter


def _classify_category(raw: Optional[str]) -> str:
    """Map a free-form recipe category into one of the frontend meal categories."""
    value = (raw or "").strip().lower()
    breakfast_words = ("breakfast", "kahvalt", "kahvalti")
    snack_words = ("snack", "atistir", "atıştır", "dessert", "tatli", "tatlı", "icecek", "içecek", "drink")
    side_words = ("side", "salad", "salata", "meze", "garnitur", "garnitür", "corba", "çorba", "soup")
    if any(w in value for w in breakfast_words):
        return "breakfast"
    if any(w in value for w in snack_words):
        return "snack"
    if any(w in value for w in side_words):
        return "side"
    return "main"


def _is_truthy(flag) -> bool:
    """Treat integer/boolean flags uniformly (1/True == suitable)."""
    if flag is None:
        return False
    return bool(flag)


def _reasons_for(recipe: Recipe, season_col: str, health_col: Optional[str], budget: Optional[str]) -> list[str]:
    reasons: list[str] = []
    if _is_truthy(getattr(recipe, season_col, None)):
        season_label = {
            "ilkbahar": "spring",
            "yaz": "summer",
            "sonbahar": "autumn",
            "kis": "winter",
        }[season_col]
        reasons.append(f"In season for {season_label}")
    if health_col and _is_truthy(getattr(recipe, health_col, None)):
        reasons.append(f"Suitable for {health_col.replace('_', ' ')}")
    if budget and recipe.maliyet_norm is not None:
        reasons.append(f"Fits your {budget} budget preference")
    if recipe.protein_g_pp and recipe.protein_g_pp >= 20:
        reasons.append("High in protein")
    if recipe.fiber_g_pp and recipe.fiber_g_pp >= 6:
        reasons.append("Good source of fibre")
    if not reasons:
        reasons.append("Balanced nutritional profile")
    return reasons


def _to_meal(recipe: Recipe, category: str, reasons: list[str]) -> MealOut:
    title = f"{(recipe.category or 'Recipe').title()} #{recipe.recipe_id}"
    return MealOut(
        id=str(recipe.recipe_id),
        title=title,
        image=f"https://placehold.co/600x400?text=Recipe+{recipe.recipe_id}",
        calories=round(recipe.calories_pp or 0, 1),
        protein=round(recipe.protein_g_pp or 0, 1),
        carbs=round(recipe.carbs_g_pp or 0, 1),
        fat=round(recipe.fat_g_pp or 0, 1),
        description=(
            f"A {category} dish (category: {recipe.category or 'n/a'}) providing "
            f"{round(recipe.calories_pp or 0)} kcal per serving."
        ),
        recommendationReasons=reasons,
        category=category,  # type: ignore[arg-type]
    )


def build_model_payload(user: User, recipes: list[Recipe]) -> dict:
    """Assemble the payload that will be sent to the AI model once it is ready.

    Bundles the user profile together with the normalised recipe feature vectors.
    """
    profile = user.profile
    return {
        "profile": {
            "age": getattr(profile, "age", None),
            "gender": getattr(profile, "gender", None),
            "height_cm": getattr(profile, "height_cm", None),
            "weight_kg": getattr(profile, "weight_kg", None),
            "activity_level": getattr(profile, "activity_level", None),
            "weight_goal": getattr(profile, "weight_goal", None),
            "vegetarian": getattr(profile, "vegetarian", None),
            "vegan": getattr(profile, "vegan", None),
            "price_preference": getattr(profile, "price_preference", None),
        },
        "recipes": [
            {
                "recipe_id": r.recipe_id,
                "category": r.category,
                "calories_pp_norm99": r.calories_pp_norm99,
                "protein_g_pp_norm99": r.protein_g_pp_norm99,
                "fat_g_pp_norm99": r.fat_g_pp_norm99,
                "carbs_g_pp_norm99": r.carbs_g_pp_norm99,
                "fiber_g_pp_norm99": r.fiber_g_pp_norm99,
                "sugar_g_pp_norm99": r.sugar_g_pp_norm99,
                "sodium_mg_pp_norm99": r.sodium_mg_pp_norm99,
                "calcium_mg_pp_norm99": r.calcium_mg_pp_norm99,
                "iron_mg_pp_norm99": r.iron_mg_pp_norm99,
                "potassium_mg_pp_norm99": r.potassium_mg_pp_norm99,
            }
            for r in recipes
        ],
    }


def _filter_recipes(
    recipes: list[Recipe], season_col: str, health_col: Optional[str], budget: Optional[str]
) -> list[Recipe]:
    """Apply soft filters; if a filter removes everything, it is relaxed."""
    pool = recipes

    seasonal = [r for r in pool if _is_truthy(getattr(r, season_col, None))]
    if seasonal:
        pool = seasonal

    if health_col:
        healthy = [r for r in pool if _is_truthy(getattr(r, health_col, None))]
        if healthy:
            pool = healthy

    ceiling = BUDGET_CEILINGS.get((budget or "").lower())
    if ceiling is not None:
        affordable = [
            r for r in pool if r.maliyet_norm is None or r.maliyet_norm <= ceiling
        ]
        if affordable:
            pool = affordable

    return pool


def generate_weekly_plan(
    db: Session,
    user: User,
    week_start: Optional[str] = None,
    health_condition: Optional[str] = None,
) -> WeeklyMealPlanOut:
    """Generate a personalised 7-day plan (placeholder until the model is ready)."""
    if week_start:
        try:
            start_date = datetime.fromisoformat(week_start).date()
        except ValueError:
            start_date = date.today()
    else:
        start_date = date.today()

    season_col = _season_column_for(start_date)
    health_col = HEALTH_CONDITION_COLUMNS.get((health_condition or "").strip().lower())
    budget = getattr(user.profile, "price_preference", None)

    all_recipes = list(db.execute(select(Recipe)).scalars())
    pool = _filter_recipes(all_recipes, season_col, health_col, budget)

    # Group the candidate pool by frontend meal category.
    by_category: dict[str, list[Recipe]] = {"breakfast": [], "main": [], "side": [], "snack": []}
    for recipe in pool:
        by_category[_classify_category(recipe.category)].append(recipe)

    # Deterministic shuffling so the same user/week yields the same plan.
    rng = random.Random(f"{user.id}-{start_date.isoformat()}")

    def pick(category: str) -> Optional[Recipe]:
        candidates = by_category.get(category) or pool
        if not candidates:
            return None
        return rng.choice(candidates)

    days: list[DayPlanOut] = []
    for offset in range(7):
        day_date = start_date + timedelta(days=offset)

        def meal(cat: str) -> Optional[MealOut]:
            recipe = pick(cat)
            if recipe is None:
                return None
            return _to_meal(recipe, cat, _reasons_for(recipe, season_col, health_col, budget))

        breakfast = meal("breakfast") or meal("main")
        lunch_main = meal("main")
        dinner_main = meal("main")
        snack = meal("snack") or meal("side") or meal("main")

        # A plan needs at least the required slots; skip the day if the pool is empty.
        if not (breakfast and lunch_main and dinner_main and snack):
            continue

        days.append(
            DayPlanOut(
                id=f"day-{offset + 1}",
                dayName=DAY_NAMES[day_date.weekday()],
                date=day_date.isoformat(),
                meals=DayMealsOut(
                    breakfast=breakfast,
                    lunchMain=lunch_main,
                    lunchSide=meal("side"),
                    dinnerMain=dinner_main,
                    dinnerSide=meal("side"),
                    snack=snack,
                ),
            )
        )

    return WeeklyMealPlanOut(
        id=f"plan-{user.id}-{start_date.isoformat()}",
        userId=str(user.id),
        weekStart=start_date.isoformat(),
        days=days,
    )


def get_alternatives(
    db: Session, category: str, exclude_meal_id: Optional[str] = None, limit: int = 6
) -> list[MealOut]:
    """Return alternative meals for a given category (placeholder logic)."""
    all_recipes = list(db.execute(select(Recipe)).scalars())
    matches = [r for r in all_recipes if _classify_category(r.category) == category]
    if exclude_meal_id is not None:
        matches = [r for r in matches if str(r.recipe_id) != str(exclude_meal_id)]
    return [_to_meal(r, category, _reasons_for(r, _season_column_for(date.today()), None, None)) for r in matches[:limit]]
