"""Shared FastAPI dependencies."""
from __future__ import annotations

from typing import Optional

from fastapi import Depends, Header, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import user_id_from_token
from app.models.user import User


def get_optional_user_id(authorization: Optional[str] = Header(default=None)) -> Optional[int]:
    """Read the current user id from the ``Authorization: Bearer <id>`` header.

    Returns ``None`` when no/invalid token is supplied. No authorization is
    enforced - this only identifies the caller for user-scoped endpoints.
    """
    return user_id_from_token(authorization)


def get_current_user(
    user_id: Optional[int] = Depends(get_optional_user_id),
    db: Session = Depends(get_db),
) -> User:
    """Resolve the current user, or raise 401 when not identified."""
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid authentication token.",
        )
    user = db.get(User, user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found."
        )
    return user
