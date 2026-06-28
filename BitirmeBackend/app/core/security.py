"""Very small security helpers.

The user asked for *basic* login only: no JWT and no authorization layer.
Passwords are still hashed with bcrypt (cheap, standard, avoids storing
plain-text secrets). The "token" returned at login is simply the user id as a
string, which the frontend sends back in the ``Authorization: Bearer <token>``
header so the backend can identify the current user.
"""
from __future__ import annotations

import bcrypt

# bcrypt operates on at most 72 bytes; longer passwords are truncated.
_MAX_BCRYPT_BYTES = 72


def hash_password(plain_password: str) -> str:
    """Return a bcrypt hash for the given plain-text password."""
    pw = plain_password.encode("utf-8")[:_MAX_BCRYPT_BYTES]
    return bcrypt.hashpw(pw, bcrypt.gensalt()).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Check a plain-text password against its stored bcrypt hash."""
    try:
        pw = plain_password.encode("utf-8")[:_MAX_BCRYPT_BYTES]
        return bcrypt.checkpw(pw, hashed_password.encode("utf-8"))
    except (ValueError, TypeError):
        return False


def create_token(user_id: int) -> str:
    """Create the opaque login token (just the user id, no signing)."""
    return str(user_id)


def user_id_from_token(token: str | None) -> int | None:
    """Parse a user id out of the opaque token, or ``None`` if invalid."""
    if not token:
        return None
    token = token.strip()
    if token.lower().startswith("bearer "):
        token = token[7:].strip()
    try:
        return int(token)
    except (TypeError, ValueError):
        return None
