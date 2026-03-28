"""
memory/retriever.py

Unified memory retriever — the agent's single point of contact for all memory.

Instead of the agent calling short_term, episodic, and semantic separately,
it calls retriever.get_context(task) and receives a single formatted string
ready to inject into the system prompt.
"""

from __future__ import annotations

from config.logging import get_logger
from memory.episodic import EpisodicMemory
from memory.semantic import SemanticMemory
from memory.short_term import ShortTermMemory

logger = get_logger(__name__)


class MemoryRetriever:
    """
    Aggregates all memory types into a single context block.

    Usage:
        retriever = MemoryRetriever(episodic_mem, semantic_mem)
        context = retriever.get_context("draft a reply to John's email")
    """

    def __init__(
        self,
        episodic: EpisodicMemory,
        semantic: SemanticMemory,
    ) -> None:
        self.episodic = episodic
        self.semantic = semantic

    def get_context(
        self,
        task: str,
        current_session_id: str | None = None,
        semantic_results: int = 4,
        recent_events: int = 10,
    ) -> str:
        """
        Build a memory context block for the given task.

        Pulls from:
        1. Semantic memory — relevant facts/preferences
        2. Recent episodic events — what the agent has been doing lately

        Returns a formatted string or empty string if nothing relevant found.
        """
        sections: list[str] = []

        # 1. Semantic — relevant long-term facts
        semantic_context = self.semantic.format_for_prompt(task, n_results=semantic_results)
        if semantic_context:
            sections.append(f"Relevant facts and preferences:\n{semantic_context}")

        # 2. Recent episodic events (not the current session — that's in short-term)
        if current_session_id:
            recent = self.episodic.get_recent(limit=recent_events)
            # Filter to events from other sessions only
            other_session_events = [
                e for e in recent if e.session_id != current_session_id
            ]
            if other_session_events:
                lines = []
                for event in other_session_events[-5:]:  # Last 5 relevant events
                    lines.append(f"- [{event.event_type}] {event.content[:120]}")
                sections.append(f"Recent agent activity:\n" + "\n".join(lines))

        if not sections:
            return ""

        return "\n\n".join(sections)

    def consolidate_session(
        self,
        session_id: str,
        summary: str,
        metadata: dict | None = None,
    ) -> str:
        """
        After a session completes, store a summary in semantic memory
        so the agent can recall what it did in this session later.
        """
        doc_id = self.semantic.store(
            text=summary,
            metadata={
                "type": "session_summary",
                "session_id": session_id,
                **(metadata or {}),
            },
            doc_id=f"session_{session_id}",
        )
        logger.info("session_consolidated", session_id=session_id, doc_id=doc_id)
        return doc_id
