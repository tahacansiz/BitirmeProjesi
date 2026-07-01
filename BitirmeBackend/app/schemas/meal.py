"""Meal / weekly-plan schemas.

These mirror the frontend ``Meal``, ``DayPlan`` and ``WeeklyMealPlan`` types
(see ``src/types/meal.ts`` in the frontend project).
"""
from __future__ import annotations

from typing import Literal, Optional

from pydantic import BaseModel

MealCategory = Literal["breakfast", "main", "side", "snack"]


class RecipeDetailOut(BaseModel):
    id: str
    title: str
    ingredients: list[str] = []   # parsed: ["4 yemek kaşığı un", ...]
    instructions: list[str] = []  # parsed: ["Adım 1 metni", ...]
    prepTimeMin: Optional[int] = None
    cookTimeMin: Optional[int] = None
    servings: Optional[int] = None
    calories: float
    protein: float
    carbs: float
    fat: float


class MealOut(BaseModel):
    id: str
    title: str
    image: str
    calories: float
    protein: float
    carbs: float
    fat: float
    description: str
    recommendationReasons: list[str]
    category: MealCategory


class DayMealsOut(BaseModel):
    breakfast: MealOut
    lunchMain: Optional[MealOut] = None
    lunchSide: Optional[MealOut] = None
    dinnerMain: Optional[MealOut] = None
    dinnerSide: Optional[MealOut] = None
    snack: Optional[MealOut] = None


class DayPlanOut(BaseModel):
    id: str
    dayName: str
    date: str
    meals: DayMealsOut


class WeeklyMealPlanOut(BaseModel):
    id: str
    userId: Optional[str] = None
    weekStart: str
    days: list[DayPlanOut]


class SaveMealPlanRequest(BaseModel):
    weekStart: Optional[str] = None
    plan: dict
