"""
api/routes/agent.py

Agent endpoints:
  POST /agent/run        — run a task
  GET  /agent/sessions   — list recent sessions
  GET  /agent/session/{id} — get full event log for a session
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from agent.executor import build_agent
from agent.core import TwinAgent
from api.schemas import (
    EventLog,
    RecentSessionsResponse,
    RunTaskRequest,
    RunTaskResponse,
    SessionEvent,
    SessionHistoryResponse,
)
from config.logging import get_logger
from memory.episodic import EpisodicMemory

logger = get_logger(__name__)
router = APIRouter(prefix="/agent", tags=["agent"])

# Module-level agent instance — built once, reused across requests
_agent: TwinAgent | None = None
_episodic: EpisodicMemory | None = None


def get_agent() -> TwinAgent:
    global _agent
    if _agent is None:
        _agent = build_agent()
    return _agent


def get_episodic() -> EpisodicMemory:
    global _episodic
    if _episodic is None:
        _episodic = EpisodicMemory()
    return _episodic


@router.post("/run", response_model=RunTaskResponse)
async def run_task(request: RunTaskRequest, agent: TwinAgent = Depends(get_agent)):
    """
    Run a task with the agent.

    The agent will think, use tools, and return a final answer.
    All steps are logged and returned in the `events` field.
    """
    logger.info("api_run_task", task_preview=request.task[:80])

    result = await agent.run(task=request.task, session_id=request.session_id)

    return RunTaskResponse(
        session_id=result.session_id,
        task=result.task,
        answer=result.answer,
        success=result.success,
        iterations=result.iterations,
        duration_seconds=result.duration_seconds,
        events=[EventLog(**e) for e in result.events],
        error=result.error,
    )


@router.get("/sessions", response_model=RecentSessionsResponse)
def list_sessions(
    limit: int = 20,
    episodic: EpisodicMemory = Depends(get_episodic),
):
    """Return the most recent session IDs."""
    sessions = episodic.get_sessions(limit=limit)
    return RecentSessionsResponse(sessions=sessions)


@router.get("/session/{session_id}", response_model=SessionHistoryResponse)
def get_session(
    session_id: str,
    episodic: EpisodicMemory = Depends(get_episodic),
):
    """Return the full event log for a specific session."""
    events = episodic.get_session(session_id)
    if not events:
        raise HTTPException(status_code=404, detail=f"Session '{session_id}' not found")

    return SessionHistoryResponse(
        session_id=session_id,
        events=[
            SessionEvent(
                id=e.id,
                session_id=e.session_id,
                event_type=e.event_type,
                content=e.content,
                created_at=e.created_at,
            )
            for e in events
        ],
        total=len(events),
    )
