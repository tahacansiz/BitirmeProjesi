"""User & profile schemas.

These map the database columns to the camelCase shapes the React frontend
expects (see ``src/types/auth.ts`` in the frontend project).
"""
from __future__ import annotations

from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.models.user import User
from app.models.user_profile import UserProfile


class UserProfileOut(BaseModel):
    """Matches the frontend ``UserProfile`` type."""

    model_config = ConfigDict(populate_by_name=True)

    age: Optional[int] = None
    height: Optional[float] = None
    weight: Optional[float] = None
    gender: Optional[str] = None
    activityLevel: Optional[str] = None
    weightGoal: Optional[str] = None
    healthCondition: str = "No conditions"
    budgetPreference: Optional[str] = None
    foodPreferences: list[str] = Field(default_factory=list)
    updatedAt: Optional[str] = None


class UserProfileUpdate(BaseModel):
    """Incoming profile update (all fields optional).

    Accepts the frontend camelCase payload. ``healthCondition`` is accepted but
    not persisted, because the provided ``user_profiles`` schema has no column
    for it (see README).
    """

    age: Optional[int] = None
    height: Optional[float] = None
    weight: Optional[float] = None
    gender: Optional[str] = None
    activityLevel: Optional[str] = None
    weightGoal: Optional[str] = None
    budgetPreference: Optional[str] = None
    healthCondition: Optional[str] = None
    foodPreferences: Optional[list[str]] = None
    # Allow direct vegetarian/vegan booleans too
    vegetarian: Optional[bool] = None
    vegan: Optional[bool] = None


class UserOut(BaseModel):
    """Matches the frontend ``User`` type."""

    id: str
    email: EmailStr
    firstName: Optional[str] = None
    lastName: Optional[str] = None
    isOnboarded: bool = False
    profile: Optional[UserProfileOut] = None


def serialize_profile(profile: UserProfile | None) -> Optional[UserProfileOut]:
    """Convert a ``UserProfile`` ORM row into the frontend-facing shape."""
    if profile is None:
        return None

    food_preferences: list[str] = []
    if profile.vegan:
        food_preferences.append("Vegan")
    elif profile.vegetarian:
        food_preferences.append("Vegetarian")

    return UserProfileOut(
        age=profile.age,
        height=profile.height_cm,
        weight=profile.weight_kg,
        gender=profile.gender,
        activityLevel=profile.activity_level,
        weightGoal=profile.weight_goal,
        budgetPreference=profile.price_preference,
        foodPreferences=food_preferences,
        updatedAt=profile.updated_at.isoformat() if profile.updated_at else None,
    )


def serialize_user(user: User) -> UserOut:
    """Convert a ``User`` ORM row (with optional profile) into the API shape."""
    return UserOut(
        id=str(user.id),
        email=user.email,
        firstName=user.first_name,
        lastName=user.last_name,
        isOnboarded=user.is_onboarded,
        profile=serialize_profile(user.profile),
    )
