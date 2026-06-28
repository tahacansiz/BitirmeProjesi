"""Meal / weekly-plan schemas.

These mirror the frontend ``Meal``, ``DayPlan`` and ``WeeklyMealPlan`` types
(see ``src/types/meal.ts`` in the frontend project).
"""
from __future__ import annotations

from typing import Literal, Optional

from pydantic import BaseModel

MealCategory = Literal["breakfast", "main", "side", "snack"]


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
    lunchMain: MealOut
    lunchSide: Optional[MealOut] = None
    dinnerMain: MealOut
    dinnerSide: Optional[MealOut] = None
    snack: MealOut


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
