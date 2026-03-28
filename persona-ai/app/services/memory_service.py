"""Memory ingestion (chunk → embed → store) and listing."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import Select, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.memory import Memory
from app.models.persona import Persona
from app.schemas.memory import MemoryIngest, MemoryRead, MemorySourceType
from app.services.embedding_service import EmbeddingService
from app.utils.chunking import chunk_text


class MemoryService:
    def __init__(self, db: AsyncSession, embeddings: EmbeddingService) -> None:
        self._db = db
        self._embeddings = embeddings

    async def ingest(self, persona: Persona, payload: MemoryIngest) -> list[MemoryRead]:
        source = payload.source_type.value
        chunks = chunk_text(payload.content)
        if not chunks:
            raise ValueError("Empty content after normalization")

        vectors = await self._embeddings.embed_texts(chunks)
        created: list[Memory] = []
        for idx, (text, vec) in enumerate(zip(chunks, vectors, strict=True)):
            mem = Memory(
                persona_id=persona.id,
                source_type=source,
                content=text,
                chunk_index=idx,
                source_ref=payload.source_ref,
                extra=payload.extra,
                embedding=vec,
            )
            self._db.add(mem)
            created.append(mem)
        await self._db.commit()
        for m in created:
            await self._db.refresh(m)
        return [MemoryRead.model_validate(m) for m in created]

    async def list_for_persona(
        self,
        persona_id: UUID,
        *,
        offset: int = 0,
        limit: int = 50,
        source_type: MemorySourceType | None = None,
    ) -> tuple[list[MemoryRead], int]:
        filters = [Memory.persona_id == persona_id]
        if source_type is not None:
            filters.append(Memory.source_type == source_type.value)

        count_stmt = select(func.count()).select_from(Memory).where(*filters)
        total = int((await self._db.execute(count_stmt)).scalar_one())

        stmt: Select = (
            select(Memory).where(*filters).order_by(Memory.created_at.desc()).offset(offset).limit(limit)
        )
        result = await self._db.execute(stmt)
        rows = list(result.scalars().all())
        return [MemoryRead.model_validate(m) for m in rows], total

    async def delete(self, memory_id: UUID, persona_id: UUID) -> bool:
        result = await self._db.execute(
            select(Memory).where(Memory.id == memory_id, Memory.persona_id == persona_id)
        )
        mem = result.scalar_one_or_none()
        if mem is None:
            return False
        await self._db.delete(mem)
        await self._db.commit()
        return True
