"""User registration, JWT token, and profile."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.exc import IntegrityError

from app.core.config import get_settings
from app.core.logging import get_logger
from app.core.security import create_access_token
from app.dependencies import CurrentUser, DbSession, limiter
from app.models.user import User
from app.schemas.user import Token, UserCreate, UserLogin, UserRead
from app.services.user_service import UserService

logger = get_logger(__name__)
_settings = get_settings()

router = APIRouter(prefix="/users", tags=["users"])


def get_user_service(db: DbSession) -> UserService:
    return UserService(db)


UserServiceDep = Annotated[UserService, Depends(get_user_service)]


@router.post(
    "/register",
    response_model=UserRead,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
)
@limiter.limit(_settings.rate_limit_auth)
async def register_user(
    request: Request,
    body: UserCreate,
    users: UserServiceDep,
) -> User:
    try:
        user = await users.create_user(email=body.email, password=body.password)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": "invalid_password", "message": str(e)},
        ) from e
    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={"code": "email_exists", "message": "Email already registered"},
        ) from None
    logger.info("user_registered", extra={"user_id": str(user.id)})
    return user


@router.post(
    "/token",
    response_model=Token,
    summary="OAuth2 password flow (form body — use in Swagger)",
)
@limiter.limit(_settings.rate_limit_auth)
async def login_form(
    request: Request,
    form: Annotated[OAuth2PasswordRequestForm, Depends()],
    users: UserServiceDep,
) -> Token:
    user = await users.authenticate(email=form.username, password=form.password)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": "invalid_credentials", "message": "Incorrect email or password"},
            headers={"WWW-Authenticate": "Bearer"},
        )
    token = create_access_token(subject=user.id)
    return Token(access_token=token)


@router.post(
    "/login",
    response_model=Token,
    summary="JSON login (same as token, for non-form clients)",
)
@limiter.limit(_settings.rate_limit_auth)
async def login_json(
    request: Request,
    body: UserLogin,
    users: UserServiceDep,
) -> Token:
    user = await users.authenticate(email=str(body.email), password=body.password)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": "invalid_credentials", "message": "Incorrect email or password"},
            headers={"WWW-Authenticate": "Bearer"},
        )
    token = create_access_token(subject=user.id)
    return Token(access_token=token)


@router.get("/me", response_model=UserRead, summary="Current user profile")
@limiter.limit(_settings.rate_limit_default)
async def read_me(request: Request, current: CurrentUser) -> User:
    return current
