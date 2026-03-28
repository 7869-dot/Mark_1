"""Vector retrieval over persona long-term memory."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import Select, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.memory import Memory
from app.schemas.memory import MemorySourceType, RetrievedMemoryChunk
from app.services.embedding_service import EmbeddingService
from app.utils.vector_search import cosine_similarity_from_distance


class RetrievalService:
    def __init__(self, db: AsyncSession, embeddings: EmbeddingService) -> None:
        self._db = db
        self._embeddings = embeddings

    async def retrieve(
        self,
        *,
        persona_id: UUID,
        query: str,
        limit: int,
        source_types: list[MemorySourceType] | None,
    ) -> list[RetrievedMemoryChunk]:
        query_vec = await self._embeddings.embed_text(query)
        distance_expr = Memory.embedding.cosine_distance(query_vec).label("distance")
        stmt: Select = select(Memory, distance_expr).where(Memory.persona_id == persona_id)
        if source_types:
            stmt = stmt.where(
                Memory.source_type.in_([s.value for s in source_types]),
            )
        stmt = stmt.order_by(distance_expr.asc()).limit(limit)
        result = await self._db.execute(stmt)
        rows = result.all()
        out: list[RetrievedMemoryChunk] = []
        for memory, distance in rows:
            d = float(distance)
            score = cosine_similarity_from_distance(d)
            out.append(
                RetrievedMemoryChunk(
                    id=memory.id,
                    content=memory.content,
                    source_type=memory.source_type,
                    chunk_index=memory.chunk_index,
                    source_ref=memory.source_ref,
                    extra=memory.extra,
                    score=score,
                )
            )
        return out
