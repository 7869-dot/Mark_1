"""
api/schemas.py

All request and response shapes for the FastAPI layer.
Your co-founder's frontend talks to these endpoints — keep them stable.

Every field has a description so the auto-generated /docs page
is useful for the frontend team without needing extra documentation.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


# ── Requests ──────────────────────────────────────────────────────────────────

class RunTaskRequest(BaseModel):
    task: str = Field(
        ...,
        description="Natural language task for the agent to execute",
        examples=["Read my last 5 emails and summarize them"],
        min_length=1,
        max_length=4000,
    )
    session_id: str | None = Field(
        None,
        description="Optional session ID to continue a previous session. Auto-generated if not provided.",
    )


class MemorySearchRequest(BaseModel):
    query: str = Field(
        ...,
        description="Natural language query to search semantic memory",
        min_length=1,
    )
    n_results: int = Field(5, ge=1, le=20, description="Number of results to return")


class MemoryStoreRequest(BaseModel):
    text: str = Field(..., description="Text to store in semantic memory", min_length=1)
    metadata: dict[str, Any] = Field(default_factory=dict, description="Optional key-value metadata")


# ── Responses ─────────────────────────────────────────────────────────────────

class EventLog(BaseModel):
    type: str
    content: str | None = None
    tool: str | None = None
    input: dict | None = None
    iteration: int | None = None


class RunTaskResponse(BaseModel):
    session_id: str
    task: str
    answer: str
    success: bool
    iterations: int
    duration_seconds: float
    events: list[EventLog] = Field(default_factory=list)
    error: str | None = None


class MemorySearchResult(BaseModel):
    id: str
    text: str
    metadata: dict[str, Any]
    distance: float
    similarity: float  # 1 - distance, easier to read


class MemorySearchResponse(BaseModel):
    query: str
    results: list[MemorySearchResult]
    total: int


class MemoryStoreResponse(BaseModel):
    id: str
    message: str


class SessionEvent(BaseModel):
    id: int
    session_id: str
    event_type: str
    content: str
    created_at: datetime | None


class SessionHistoryResponse(BaseModel):
    session_id: str
    events: list[SessionEvent]
    total: int


class RecentSessionsResponse(BaseModel):
    sessions: list[str]


class HealthResponse(BaseModel):
    status: str
    agent_name: str
    model: str
    tools_available: int
    memory_entries: int
    version: str = "0.1.0"
