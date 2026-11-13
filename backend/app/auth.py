"""Authentication: verify Neon Auth (Managed Better Auth) JWTs.

The browser never talks to this API. The Next.js server gets a short-lived JWT for the
signed-in user (`auth.token()`) and forwards it as `Authorization: Bearer <jwt>`.
We verify it against the auth server's JWKS (EdDSA) and map `sub` to `users.id`.
"""

from functools import lru_cache
from typing import Annotated
from urllib.parse import urlsplit

import jwt
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jwt import PyJWKClient
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.config import settings
from app.db import get_db
from app.models import User

_bearer = HTTPBearer(auto_error=False)
_UNAUTHENTICATED = {"WWW-Authenticate": "Bearer"}


def _issuer() -> str | None:
    """Neon sets `iss` and `aud` to the auth host's origin, without the `/<db>/auth` path."""
    if not settings.neon_auth_base_url:
        return None
    parts = urlsplit(settings.neon_auth_base_url)
    return f"{parts.scheme}://{parts.netloc}"


@lru_cache(maxsize=1)
def _jwks() -> PyJWKClient:
    # PyJWKClient caches the keys and re-fetches when it meets an unknown `kid`.
    return PyJWKClient(settings.neon_auth_jwks_url, cache_keys=True)


def decode_token(token: str) -> dict:
    """Verify signature, expiry, issuer and audience. Raises 401/503 `HTTPException`."""
    issuer = _issuer()
    if issuer is None or not settings.neon_auth_jwks_url:
        raise HTTPException(503, "Authentication is not configured")
    try:
        key = _jwks().get_signing_key_from_jwt(token).key
        return jwt.decode(
            token,
            key,
            algorithms=["EdDSA"],
            issuer=issuer,
            audience=issuer,
            options={"require": ["exp", "iat", "sub"]},
        )
    except jwt.PyJWKClientConnectionError as exc:
        raise HTTPException(503, "Could not reach the authentication server") from exc
    except jwt.PyJWTError as exc:
        raise HTTPException(401, "Invalid or expired token", headers=_UNAUTHENTICATED) from exc


def _display_name(claims: dict) -> str:
    name = str(claims.get("name") or "").strip()
    return (name or str(claims["email"]).split("@")[0])[:120]


def _get_or_create_user(db: Session, claims: dict) -> User:
    """The app `users` row shares its id with the auth user; create it on first sight."""
    user = db.get(User, claims["sub"])
    if user is not None:
        return user

    email = str(claims.get("email") or "").strip().lower()
    if not email:
        raise HTTPException(401, "Token has no email", headers=_UNAUTHENTICATED)
    claims = {**claims, "email": email}

    user = User(
        id=claims["sub"],
        name=_display_name(claims),
        email=email[:255],
        email_verified=bool(claims.get("emailVerified")),
        image=claims.get("image"),
    )
    db.add(user)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        # Two first requests raced, or the email already belongs to another account.
        existing = db.get(User, claims["sub"])
        if existing is not None:
            return existing
        raise HTTPException(409, "An account with this email already exists") from None
    return user


def current_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(_bearer)],
    db: Annotated[Session, Depends(get_db)],
) -> User:
    if credentials is None:
        raise HTTPException(401, "Not authenticated", headers=_UNAUTHENTICATED)
    return _get_or_create_user(db, decode_token(credentials.credentials))


CurrentUser = Annotated[User, Depends(current_user)]
