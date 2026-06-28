"""Authentication request/response schemas."""
from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, EmailStr

from app.schemas.user import UserOut


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    firstName: Optional[str] = None
    lastName: Optional[str] = None


class AuthResponse(BaseModel):
    """Matches the frontend ``LoginResponse`` type."""

    success: bool
    token: Optional[str] = None
    user: Optional[UserOut] = None
    message: Optional[str] = None
