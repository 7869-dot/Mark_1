"""Memory ingestion, listing, retrieval (RAG over persona)."""

from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Request, Response, status

from app.core.config import get_settings
from app.dependencies import CurrentUser, DbSession, limiter
from app.models.persona import Persona
from app.schemas.memory import (
    MemoryIngest,
    MemoryListResponse,
    MemoryRead,
    MemoryRetrieveRequest,
    MemoryRetrieveResponse,
    MemorySourceType,
)
from app.services.embedding_service import EmbeddingService
from app.services.memory_service import MemoryService
from app.services.persona_service import PersonaService
from app.services.retrieval_service import RetrievalService

_settings = get_settings()

router = APIRouter(prefix="/personas", tags=["memory"])


def get_embedding_service() -> EmbeddingService:
    return EmbeddingService()


def get_persona_service(db: DbSession) -> PersonaService:
    return PersonaService(db)


def get_memory_service(
    db: DbSession,
    emb: Annotated[EmbeddingService, Depends(get_embedding_service)],
) -> MemoryService:
    return MemoryService(db, emb)


def get_retrieval_service(
    db: DbSession,
    emb: Annotated[EmbeddingService, Depends(get_embedding_service)],
) -> RetrievalService:
    return RetrievalService(db, emb)


PersonaServiceDep = Annotated[PersonaService, Depends(get_persona_service)]
MemoryServiceDep = Annotated[MemoryService, Depends(get_memory_service)]
RetrievalServiceDep = Annotated[RetrievalService, Depends(get_retrieval_service)]


async def get_owned_persona(
    persona_id: UUID,
    current: CurrentUser,
    personas: PersonaServiceDep,
) -> Persona:
    p = await personas.get_owned(current, persona_id)
    if p is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "persona_not_found", "message": "Persona not found"},
        )
    return p


OwnedPersona = Annotated[Persona, Depends(get_owned_persona)]


@router.post(
    "/{persona_id}/memories/ingest",
    response_model=list[MemoryRead],
    status_code=status.HTTP_201_CREATED,
    summary="Chunk, embed, and store long-term memory for this persona",
)
@limiter.limit(_settings.rate_limit_default)
async def ingest_memories(
    request: Request,
    persona: OwnedPersona,
    body: MemoryIngest,
    memories: MemoryServiceDep,
) -> list[MemoryRead]:
    try:
        return await memories.ingest(persona, body)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": "ingest_error", "message": str(e)},
        ) from e
    except RuntimeError as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail={"code": "embedding_failed", "message": str(e)},
        ) from e


@router.get(
    "/{persona_id}/memories",
    response_model=MemoryListResponse,
    summary="Paginated memory listing (metadata + full text)",
)
@limiter.limit(_settings.rate_limit_default)
async def list_memories(
    request: Request,
    persona: OwnedPersona,
    memories: MemoryServiceDep,
    offset: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=200)] = 50,
    source_type: MemorySourceType | None = None,
) -> MemoryListResponse:
    items, total = await memories.list_for_persona(
        persona.id, offset=offset, limit=limit, source_type=source_type
    )
    return MemoryListResponse(total=total, offset=offset, limit=limit, items=items)


@router.post(
    "/{persona_id}/memories/retrieve",
    response_model=MemoryRetrieveResponse,
    summary="Vector search: retrieve top-k memory chunks for a query",
)
@limiter.limit(_settings.rate_limit_default)
async def retrieve_memories(
    request: Request,
    persona: OwnedPersona,
    body: MemoryRetrieveRequest,
    retrieval: RetrievalServiceDep,
) -> MemoryRetrieveResponse:
    try:
        results = await retrieval.retrieve(
            persona_id=persona.id,
            query=body.query,
            limit=body.limit,
            source_types=body.source_types,
        )
    except RuntimeError as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail={"code": "embedding_failed", "message": str(e)},
        ) from e
    return MemoryRetrieveResponse(query=body.query, results=results)


@router.delete(
    "/{persona_id}/memories/{memory_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a single memory row (all chunks are rows)",
)
@limiter.limit(_settings.rate_limit_default)
async def delete_memory(
    request: Request,
    persona: OwnedPersona,
    memory_id: UUID,
    memories: MemoryServiceDep,
) -> Response:
    ok = await memories.delete(memory_id, persona.id)
    if not ok:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "memory_not_found", "message": "Memory not found"},
        )
    return Response(status_code=status.HTTP_204_NO_CONTENT)
