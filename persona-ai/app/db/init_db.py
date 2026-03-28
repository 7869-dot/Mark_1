"""Database bootstrap helpers (extension + health)."""

from __future__ import annotations

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import get_logger

logger = get_logger(__name__)


async def ensure_vector_extension(session: AsyncSession) -> None:
    """Ensure pgvector extension exists (idempotent)."""
    await session.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
    await session.commit()
    logger.info("pgvector extension ensured")


async def ping_db(session: AsyncSession) -> bool:
    await session.execute(text("SELECT 1"))
    return True
