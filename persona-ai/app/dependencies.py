"""FastAPI dependencies: DB session, auth, and rate limiter."""

from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer, OAuth2PasswordBearer
from slowapi import Limiter
from slowapi.util import get_remote_address
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import parse_user_id_from_token
from app.db.session import get_async_session
from app.models.user import User

limiter = Limiter(key_func=get_remote_address)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/users/token", auto_error=False)
bearer_scheme = HTTPBearer(auto_error=False)

DbSession = Annotated[AsyncSession, Depends(get_async_session)]


async def get_token_from_header(
    oauth_token: Annotated[str | None, Depends(oauth2_scheme)],
    bearer: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)],
) -> str:
    if oauth_token:
        return oauth_token
    if bearer and bearer.scheme.lower() == "bearer":
        return bearer.credentials
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail={"code": "missing_token", "message": "Not authenticated"},
        headers={"WWW-Authenticate": "Bearer"},
    )


async def get_current_user(
    db: DbSession,
    token: Annotated[str, Depends(get_token_from_header)],
) -> User:
    try:
        user_id: UUID = parse_user_id_from_token(token)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": "invalid_token", "message": "Invalid or expired token"},
            headers={"WWW-Authenticate": "Bearer"},
        ) from None
    result = await db.execute(select(User).where(User.id == user_id, User.is_active.is_(True)))
    user = result.scalar_one_or_none()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": "user_not_found", "message": "User not found or inactive"},
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]
