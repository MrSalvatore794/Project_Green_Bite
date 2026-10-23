"""JWT utilities and Flask authentication/authorization helpers.

This module keeps JWT logic explicit and small. It does not access SQLite
directly; loading the authenticated user is delegated to AuthService through
the application's extension registry.
"""

from datetime import datetime, timedelta, timezone
from functools import wraps

import jwt
from flask import current_app, g, request

from services.exceptions import AuthenticationError, ForbiddenError


def generate_access_token(user_id: int, role: str) -> str:
    """Create a signed JWT carrying only minimal identity information."""
    now = datetime.now(timezone.utc)
    expires_at = now + timedelta(minutes=current_app.config["JWT_EXPIRATION_MINUTES"])
    payload = {
        "sub": str(user_id),
        "role": role,
        "iat": int(now.timestamp()),
        "exp": int(expires_at.timestamp()),
    }
    return jwt.encode(payload, current_app.config["JWT_SECRET_KEY"], algorithm="HS256")


def decode_access_token(token: str) -> dict:
    """Decode and validate a JWT, returning its payload.

    Raises ``jwt`` exceptions when the token is invalid or expired.
    """
    return jwt.decode(
        token,
        current_app.config["JWT_SECRET_KEY"],
        algorithms=["HS256"],
    )


def _extract_bearer_token() -> str:
    header = request.headers.get("Authorization")
    if not header:
        raise AuthenticationError("Please Login to access authorization.")
    parts = header.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise AuthenticationError("Invalid Authorization header.")
    return parts[1]


def require_auth(view):
    """Authenticate the request and load the current user into ``flask.g``."""

    @wraps(view)
    def wrapped(*args, **kwargs):
        token = _extract_bearer_token()
        try:
            payload = decode_access_token(token)
        except jwt.ExpiredSignatureError:
            raise AuthenticationError("Token has expired.")
        except jwt.InvalidTokenError:
            raise AuthenticationError("Invalid token.")

        user_id = payload.get("sub")
        try:
            user_id = int(user_id)
        except (TypeError, ValueError):
            raise AuthenticationError("Invalid token.")

        auth_service = current_app.extensions["auth_service"]
        g.current_user = auth_service.get_user(user_id)
        return view(*args, **kwargs)

    return wrapped


def get_current_user():
    """Return the authenticated user for the current request."""
    user = g.get("current_user")
    if user is None:
        raise AuthenticationError("Please Login to access authorization.")
    return user


def get_optional_current_user():
    """Return the current user when a valid JWT is present, otherwise None.

    Public endpoints (e.g. product detail) use this to personalise the
    response without requiring authentication.
    """
    if not request.headers.get("Authorization"):
        return None
    try:
        token = _extract_bearer_token()
        payload = decode_access_token(token)
        user_id = int(payload.get("sub"))
        return current_app.extensions["auth_service"].get_user(user_id)
    except Exception:
        return None


def require_role(role: str):
    """Require the current user to have a specific role."""

    def decorator(view):
        @wraps(view)
        def wrapped(*args, **kwargs):
            if get_current_user().role != role:
                raise ForbiddenError(
                    "You do not have permission to perform this action."
                )
            return view(*args, **kwargs)

        return wrapped

    return decorator


def require_permission(permission: str):
    """Require the current user to have a specific permission."""

    def decorator(view):
        @wraps(view)
        def wrapped(*args, **kwargs):
            if permission not in get_current_user().get_permissions():
                raise ForbiddenError(
                    "You do not have permission to perform this action."
                )
            return view(*args, **kwargs)

        return wrapped

    return decorator
