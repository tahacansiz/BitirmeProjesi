# -*- coding: utf-8 -*-
"""Weekly meal-plan generation via the MILP solver in NutritionRecommender."""
from __future__ import annotations

import sys
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Optional

import pandas as pd
from sqlalchemy.orm import Session

from app.models.user import User
from app.schemas.meal import (
    DayMealsOut,
    DayPlanOut,
    MealOut,
    WeeklyMealPlanOut,
)

# ---------------------------------------------------------------------------
# Bring NutritionRecommender onto the import path
# ---------------------------------------------------------------------------
_NR_DIR = Path(__file__).resolve().parents[3] / "NutritionRecommender"
if str(_NR_DIR) not in sys.path:
    sys.path.insert(0, str(_NR_DIR))

from meal_planner import milp_kur_ve_coz, PlanSonuc  # noqa: E402
from nutrition_targets import UserProfile as MILPProfile  # noqa: E402

# ---------------------------------------------------------------------------
# Parquet – loaded once, kept in memory
# ---------------------------------------------------------------------------
_PARQUET_PATH = _NR_DIR / "recipes_normalized.parquet"
_df_recipes: Optional[pd.DataFrame] = None


def _get_recipes_df() -> pd.DataFrame:
    global _df_recipes
    if _df_recipes is None:
        _df_recipes = pd.read_parquet(_PARQUET_PATH)
    return _df_recipes


# ---------------------------------------------------------------------------
# Field-value mappings  (frontend value → MILP expected value)
# ---------------------------------------------------------------------------
_GENDER_MAP = {
    "male": "erkek", "erkek": "erkek",
    "female": "kadin", "kadin": "kadin", "kadın": "kadin",
}

_ACTIVITY_MAP = {
    "sedentary": "sedanter", "sedanter": "sedanter",
    "light": "hafif",        "hafif": "hafif",
    "moderate": "orta",      "orta": "orta",
    "vigorous": "yogun",     "yogun": "yogun", "yoğun": "yogun",
}

_GOAL_MAP = {
    "lose": "verme",    "verme": "verme",    "weight_loss": "verme",
    "maintain": "koruma", "koruma": "koruma",
    "gain": "alma",     "alma": "alma",      "weight_gain": "alma",
}

_PRICE_MAP = {
    "low": "ucuz",    "ucuz": "ucuz",    "cheap": "ucuz",
    "medium": "orta", "orta": "orta",
    "high": "pahali", "pahali": "pahali", "expensive": "pahali",
}

# Query-param health condition label → MILP column name
_HEALTH_MAP = {
    "diabetes": "diabetes",
    "celiac": "celiac",
    "lactose intolerance": "lactose_intolerance",
    "lactose_intolerance": "lactose_intolerance",
    "hypertension": "hypertension",
    "pregnancy": "pregnancy",
    "obesity": "obesity",
    "cardiovascular disease": "cardiovascular_disease",
    "cardiovascular_disease": "cardiovascular_disease",
    "cardiovascular": "cardiovascular_disease",
    "kidney disease": "kidney_disease",
    "kidney_disease": "kidney_disease",
    "kidney": "kidney_disease",
    "liver disease": "liver_disease",
    "liver_disease": "liver_disease",
    "liver": "liver_disease",
    "anemia": "anemia",
}

DAY_NAMES = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

# MILP slot → frontend category
_SLOT_TO_CATEGORY = {
    "kahvalti":  "breakfast",
    "ogle_ana":  "main",
    "ogle_yan":  "side",
    "aksam_ana": "main",
    "aksam_yan": "side",
    "ara_ogun":  "snack",
}

# MILP slot → DayMealsOut field name
_SLOT_TO_FIELD = {
    "kahvalti":  "breakfast",
    "ogle_ana":  "lunchMain",
    "ogle_yan":  "lunchSide",
    "aksam_ana": "dinnerMain",
    "aksam_yan": "dinnerSide",
    "ara_ogun":  "snack",
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _map(mapping: dict, value: Optional[str], default: str) -> str:
    if not value:
        return default
    return mapping.get(value.strip().lower(), default)


def _build_milp_profile(user: User, health_condition: Optional[str]) -> MILPProfile:
    p = user.profile

    saglik: list[str] = []
    if health_condition:
        col = _HEALTH_MAP.get(health_condition.strip().lower())
        if col:
            saglik.append(col)

    return MILPProfile(
        yas=getattr(p, "age", None) or 30,
        cinsiyet=_map(_GENDER_MAP, getattr(p, "gender", None), "erkek"),
        boy_cm=getattr(p, "height_cm", None) or 170.0,
        kilo_kg=getattr(p, "weight_kg", None) or 70.0,
        aktivite=_map(_ACTIVITY_MAP, getattr(p, "activity_level", None), "orta"),
        kilo_hedefi=_map(_GOAL_MAP, getattr(p, "weight_goal", None), "koruma"),
        saglik_kosullari=saglik,
        vejetaryen=bool(getattr(p, "vegetarian", False)),
        vegan=bool(getattr(p, "vegan", False)),
        fiyat_tercihi=_map(_PRICE_MAP, getattr(p, "price_preference", None), "orta"),
    )


def _reasons_for(row: pd.Series, milp_profile: MILPProfile) -> list[str]:
    reasons: list[str] = []
    if row.get("protein_g_pp", 0) >= 20:
        reasons.append("High in protein")
    if row.get("fiber_g_pp", 0) >= 6:
        reasons.append("Good source of fibre")
    for cond in milp_profile.saglik_kosullari:
        score = row.get(cond, 0) or 0
        if score >= 0.6:
            reasons.append(f"Suitable for {cond.replace('_', ' ')}")
    if not reasons:
        reasons.append("Balanced nutritional profile")
    return reasons


def _row_to_meal(recipe_id, category: str, df: pd.DataFrame, milp_profile: MILPProfile) -> Optional[MealOut]:
    rows = df[df["recipe_id"] == recipe_id]
    if rows.empty:
        return None
    row = rows.iloc[0]
    return MealOut(
        id=str(recipe_id),
        title=f"{(row.get('category') or 'Recipe').title()} #{recipe_id}",
        image=f"https://placehold.co/600x400?text=Recipe+{recipe_id}",
        calories=round(float(row.get("calories_pp") or 0), 1),
        protein=round(float(row.get("protein_g_pp") or 0), 1),
        carbs=round(float(row.get("carbs_g_pp") or 0), 1),
        fat=round(float(row.get("fat_g_pp") or 0), 1),
        description=(
            f"A {category} dish providing "
            f"{round(float(row.get('calories_pp') or 0))} kcal per serving."
        ),
        recommendationReasons=_reasons_for(row, milp_profile),
        category=category,  # type: ignore[arg-type]
    )


def _determine_solver() -> str:
    """Pick the best available PuLP solver."""
    try:
        import pulp
        if pulp.HiGHS_CMD().available():
            return "HiGHS"
    except Exception:
        pass
    return "CBC"


# ---------------------------------------------------------------------------
# Public API (called by routers/meals.py)
# ---------------------------------------------------------------------------

def generate_weekly_plan(
    db: Session,
    user: User,
    week_start: Optional[str] = None,
    health_condition: Optional[str] = None,
) -> WeeklyMealPlanOut:
    if week_start:
        try:
            start_date = datetime.fromisoformat(week_start).date()
        except ValueError:
            start_date = date.today()
    else:
        start_date = date.today()

    df = _get_recipes_df()
    milp_profile = _build_milp_profile(user, health_condition)
    solver = _determine_solver()

    sonuc: PlanSonuc = milp_kur_ve_coz(
        user=milp_profile,
        df_tarifler=df,
        verbose=False,
        cozucu=solver,
    )

    if sonuc.amac_degeri is None or not sonuc.plan:
        # Fallback: return empty plan with a clear indication
        return WeeklyMealPlanOut(
            id=f"plan-{user.id}-{start_date.isoformat()}",
            userId=str(user.id),
            weekStart=start_date.isoformat(),
            days=[],
        )

    days: list[DayPlanOut] = []
    for gun in sonuc.plan:
        d = gun["gun"] - 1  # 0-indexed
        day_date = start_date + timedelta(days=d)
        ogunler = gun["ogunler"]

        def get_meal(slot: str, category: str) -> Optional[MealOut]:
            entry = ogunler.get(slot)
            if not entry:
                return None
            return _row_to_meal(entry["recipe_id"], category, df, milp_profile)

        breakfast = get_meal("kahvalti", "breakfast")
        lunch_main = get_meal("ogle_ana", "main")
        lunch_side = get_meal("ogle_yan", "side")
        dinner_main = get_meal("aksam_ana", "main")
        dinner_side = get_meal("aksam_yan", "side")
        snack = get_meal("ara_ogun", "snack")

        if not (breakfast and lunch_main and dinner_main and snack):
            continue

        days.append(
            DayPlanOut(
                id=f"day-{d + 1}",
                dayName=DAY_NAMES[day_date.weekday()],
                date=day_date.isoformat(),
                meals=DayMealsOut(
                    breakfast=breakfast,
                    lunchMain=lunch_main,
                    lunchSide=lunch_side,
                    dinnerMain=dinner_main,
                    dinnerSide=dinner_side,
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
    """Return alternative meals for a given category (from parquet directly)."""
    df = _get_recipes_df()

    cat_map = {
        "breakfast": ["Kahvaltılık", "Tost", "Sandviç", "Poğaça", "Çörek"],
        "main": ["Sebze", "Tavuk", "Et", "Makarna", "Köfte", "Pilav", "Balık",
                 "Bakliyat", "Mantı", "Deniz Ürünleri", "Sakatat", "Kebap",
                 "Sulu Yemek", "Hamburger", "Zeytinyağlı", "Dolma Sarma",
                 "Kızartma", "Pizza", "Pide", "Börek"],
        "side": ["Çorba", "Ekmek", "Meze", "Salata"],
        "snack": ["Tuzlu Atıştırmalık", "Atıştırmalık", "Tatlı Atıştırmalık",
                  "Meyveli Tatlı", "Tatlı Kek", "Tatlı Kurabiye", "Tatlı",
                  "Kek", "Kurabiye", "Sütlü Tatlı", "Diyet Tatlı"],
    }

    cats = cat_map.get(category, [])
    pool = df[df["category"].isin(cats)]
    if exclude_meal_id is not None:
        pool = pool[pool["recipe_id"] != exclude_meal_id]

    dummy_profile = MILPProfile(yas=30, cinsiyet="erkek", boy_cm=175, kilo_kg=70)
    results = []
    for _, row in pool.head(limit).iterrows():
        results.append(_row_to_meal(row["recipe_id"], category, df, dummy_profile))
    return [m for m in results if m is not None]
