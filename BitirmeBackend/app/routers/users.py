"""User profile routes."""
from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.deps import get_current_user
from app.models.user import User
from app.models.user_profile import UserProfile
from app.schemas.user import (
    UserOut,
    UserProfileUpdate,
    serialize_user,
)

router = APIRouter(prefix="/users", tags=["users"])


def _apply_profile_update(profile: UserProfile, payload: UserProfileUpdate) -> None:
    """Map the incoming camelCase payload onto the ORM columns."""
    if payload.age is not None:
        profile.age = payload.age
    if payload.gender is not None:
        profile.gender = payload.gender
    if payload.height is not None:
        profile.height_cm = payload.height
    if payload.weight is not None:
        profile.weight_kg = payload.weight
    if payload.activityLevel is not None:
        profile.activity_level = payload.activityLevel
    if payload.weightGoal is not None:
        profile.weight_goal = payload.weightGoal
    if payload.budgetPreference is not None:
        profile.price_preference = payload.budgetPreference

    # Derive vegetarian/vegan from explicit flags or from foodPreferences list.
    if payload.vegetarian is not None:
        profile.vegetarian = payload.vegetarian
    if payload.vegan is not None:
        profile.vegan = payload.vegan
    if payload.foodPreferences is not None:
        prefs = {p.strip().lower() for p in payload.foodPreferences}
        profile.vegan = "vegan" in prefs
        profile.vegetarian = profile.vegan or "vegetarian" in prefs
    # NOTE: healthCondition is intentionally not persisted - the provided
    # user_profiles schema has no column for it (see README).


def _get_or_create_profile(db: Session, user: User) -> UserProfile:
    if user.profile is None:
        user.profile = UserProfile(user_id=user.id)
        db.add(user.profile)
    return user.profile


@router.get("/profile", response_model=UserOut)
def get_profile(current_user: User = Depends(get_current_user)) -> UserOut:
    return serialize_user(current_user)


@router.put("/profile", response_model=UserOut)
def update_profile(
    payload: UserProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> UserOut:
    profile = _get_or_create_profile(db, current_user)
    _apply_profile_update(profile, payload)
    db.commit()
    db.refresh(current_user)
    return serialize_user(current_user)


@router.post("/onboarding/complete", response_model=UserOut)
def complete_onboarding(
    payload: UserProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> UserOut:
    profile = _get_or_create_profile(db, current_user)
    _apply_profile_update(profile, payload)
    current_user.is_onboarded = True
    db.commit()
    db.refresh(current_user)
    return serialize_user(current_user)
