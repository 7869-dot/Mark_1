"""
memory/episodic.py

Episodic memory — a persistent, timestamped log of everything the agent does.

Every action, observation, and task outcome is recorded here.
This is your audit trail, your debugging surface, and the raw material
for building the agent's long-term self-awareness.

Storage: SQLite locally (zero setup), swap DATABASE_URL to Postgres for prod.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from enum import Enum
from typing import Any

from sqlalchemy import (
    Column,
    DateTime,
    Integer,
    String,
    Text,
    create_engine,
    desc,
    select,
)
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from config.logging import get_logger
from config.settings import settings

logger = get_logger(__name__)


class EventType(str, Enum):
    TASK_START = "task_start"
    THOUGHT = "thought"
    ACTION = "action"
    OBSERVATION = "observation"
    TASK_COMPLETE = "task_complete"
    TASK_FAILED = "task_failed"
    MEMORY_RETRIEVED = "memory_retrieved"


class Base(DeclarativeBase):
    pass


class EpisodicEvent(Base):
    __tablename__ = "episodic_events"

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String(64), nullable=False, index=True)
    event_type = Column(String(32), nullable=False)
    content = Column(Text, nullable=False)
    metadata_json = Column(Text, default="{}")
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    @property
    def metadata(self) -> dict:
        return json.loads(self.metadata_json or "{}")


class EpisodicMemory:
    """
    Persistent log of all agent events.

    Usage:
        mem = EpisodicMemory()
        mem.log(session_id, EventType.ACTION, "Called gmail.send_email", {"to": "..."})
        events = mem.get_session(session_id)
    """

    def __init__(self) -> None:
        # Create data directory if it doesn't exist
        import os
        db_path = settings.database_url.replace("sqlite:///", "")
        os.makedirs(os.path.dirname(db_path) if os.path.dirname(db_path) else ".", exist_ok=True)

        self._engine = create_engine(
            settings.database_url,
            connect_args={"check_same_thread": False} if "sqlite" in settings.database_url else {},
        )
        Base.metadata.create_all(self._engine)
        self._Session = sessionmaker(bind=self._engine)
        logger.info("episodic_memory_init", db=settings.database_url)

    def log(
        self,
        session_id: str,
        event_type: EventType,
        content: str,
        metadata: dict[str, Any] | None = None,
    ) -> EpisodicEvent:
        """Record a single event. Returns the saved event."""
        event = EpisodicEvent(
            session_id=session_id,
            event_type=event_type.value,
            content=content,
            metadata_json=json.dumps(metadata or {}),
        )
        with self._Session() as session:
            session.add(event)
            session.commit()
            session.refresh(event)

        logger.debug(
            "episodic_log",
            session_id=session_id,
            event_type=event_type.value,
            content_preview=content[:80],
        )
        return event

    def get_session(self, session_id: str, limit: int = 200) -> list[EpisodicEvent]:
        """Return all events for a given session, oldest first."""
        with self._Session() as session:
            stmt = (
                select(EpisodicEvent)
                .where(EpisodicEvent.session_id == session_id)
                .order_by(EpisodicEvent.created_at)
                .limit(limit)
            )
            return list(session.scalars(stmt))

    def get_recent(self, limit: int = 50) -> list[EpisodicEvent]:
        """Return the most recent events across all sessions."""
        with self._Session() as session:
            stmt = (
                select(EpisodicEvent)
                .order_by(desc(EpisodicEvent.created_at))
                .limit(limit)
            )
            return list(session.scalars(stmt))

    def get_sessions(self, limit: int = 20) -> list[str]:
        """Return the most recent unique session IDs."""
        with self._Session() as session:
            from sqlalchemy import distinct, func
            stmt = (
                select(EpisodicEvent.session_id)
                .group_by(EpisodicEvent.session_id)
                .order_by(func.max(EpisodicEvent.created_at).desc())
                .limit(limit)
            )
            return list(session.scalars(stmt))

    def format_session_for_context(self, session_id: str) -> str:
        """
        Format a session's events as readable text for injecting into prompts.
        Used when the agent wants to recall what it did in a previous session.
        """
        events = self.get_session(session_id)
        if not events:
            return "No events found for this session."

        lines = [f"Session: {session_id}"]
        for event in events:
            ts = event.created_at.strftime("%H:%M:%S") if event.created_at else "?"
            lines.append(f"[{ts}] {event.event_type.upper()}: {event.content}")

        return "\n".join(lines)
