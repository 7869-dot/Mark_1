"""FastAPI application: Persona AI API."""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from app.core.config import get_settings
from app.core.logging import get_logger, setup_logging
from app.db.init_db import ping_db
from app.db.session import AsyncSessionLocal
from app.dependencies import limiter
from app.routers import memory, persona, user

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging(logging.DEBUG if get_settings().debug else logging.INFO)
    yield


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title=settings.app_name,
        description=(
            "Personal AI Persona API — users, digital twins (personas), long-term memory "
            "with pgvector, and retrieval for agentic behavior."
        ),
        version="0.1.0",
        lifespan=lifespan,
        openapi_url=f"{settings.api_v1_prefix}/openapi.json",
        docs_url=f"{settings.api_v1_prefix}/docs",
        redoc_url=f"{settings.api_v1_prefix}/redoc",
    )

    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request,
        exc: RequestValidationError,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=422,
            content={
                "detail": exc.errors(),
                "message": "Request validation failed",
            },
        )

    origins = settings.cors_origin_list
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_middleware(SlowAPIMiddleware)

    app.include_router(user.router, prefix=settings.api_v1_prefix)
    app.include_router(persona.router, prefix=settings.api_v1_prefix)
    app.include_router(memory.router, prefix=settings.api_v1_prefix)

    @app.get("/health", tags=["health"], summary="Liveness probe")
    async def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.get(f"{settings.api_v1_prefix}/ready", tags=["health"], summary="DB readiness")
    async def ready() -> dict[str, str]:
        try:
            async with AsyncSessionLocal() as session:
                await ping_db(session)
        except Exception:
            logger.exception("readiness_failed")
            raise HTTPException(
                status_code=503,
                detail={"status": "not_ready"},
            ) from None
        return {"status": "ready"}

    return app


app = create_app()
