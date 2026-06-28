"""Authentication routes (basic email/password login, no JWT)."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import create_token, hash_password, verify_password
from app.models.user import User
from app.schemas.auth import AuthResponse, LoginRequest, RegisterRequest
from app.schemas.user import serialize_user

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=AuthResponse)
def register(payload: RegisterRequest, db: Session = Depends(get_db)) -> AuthResponse:
    existing = db.execute(select(User).where(User.email == payload.email)).scalar_one_or_none()
    if existing is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Email is already registered."
        )

    user = User(
        email=payload.email,
        password_hash=hash_password(payload.password),
        first_name=payload.firstName,
        last_name=payload.lastName,
        is_onboarded=False,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    return AuthResponse(success=True, token=create_token(user.id), user=serialize_user(user))


@router.post("/login", response_model=AuthResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)) -> AuthResponse:
    user = db.execute(select(User).where(User.email == payload.email)).scalar_one_or_none()
    if user is None or not verify_password(payload.password, user.password_hash):
        return AuthResponse(success=False, message="Invalid email or password.")

    return AuthResponse(success=True, token=create_token(user.id), user=serialize_user(user))


@router.post("/logout", response_model=AuthResponse)
def logout() -> AuthResponse:
    # With the basic token scheme there is no server-side session to clear;
    # the frontend simply discards the stored token.
    return AuthResponse(success=True, message="Logged out.")


@router.post("/refresh", response_model=AuthResponse)
def refresh(db: Session = Depends(get_db)) -> AuthResponse:
    # Tokens never expire in the basic scheme, so refresh is a no-op kept for
    # frontend compatibility.
    return AuthResponse(success=True, message="Token still valid.")
