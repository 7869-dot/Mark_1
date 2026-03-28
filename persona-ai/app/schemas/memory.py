"""Memory ingestion and retrieval schemas."""

from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class MemorySourceType(StrEnum):
    profile = "profile"
    document = "document"
    chat = "chat"


class MemoryIngest(BaseModel):
    source_type: MemorySourceType
    content: str = Field(min_length=1, max_length=500_000)
    source_ref: str | None = Field(default=None, max_length=512)
    extra: dict[str, Any] | None = None


class MemoryRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    persona_id: UUID
    source_type: str
    content: str
    chunk_index: int
    source_ref: str | None
    extra: dict[str, Any] | None
    created_at: datetime


class MemoryRetrieveRequest(BaseModel):
    query: str = Field(min_length=1, max_length=8000)
    limit: int = Field(default=8, ge=1, le=50)
    source_types: list[MemorySourceType] | None = None


class RetrievedMemoryChunk(BaseModel):
    id: UUID
    content: str
    source_type: str
    chunk_index: int
    source_ref: str | None
    extra: dict[str, Any] | None
    score: float = Field(description="Cosine similarity 0–1 (higher is closer)")


class MemoryRetrieveResponse(BaseModel):
    query: str
    results: list[RetrievedMemoryChunk]


class MemoryListResponse(BaseModel):
    total: int
    offset: int
    limit: int
    items: list[MemoryRead]
