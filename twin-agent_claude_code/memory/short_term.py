"""
memory/short_term.py

Manages the agent's in-context conversation window.

Responsibility: keep messages within the token budget by evicting old messages
when the window fills up. The system prompt and the most recent user message
are always preserved — only middle history gets trimmed.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone

from config.logging import get_logger
from config.settings import settings
from llm.client import llm_client

logger = get_logger(__name__)

# Reserve this many tokens for the LLM's output
OUTPUT_TOKEN_BUDGET = 4096


@dataclass
class Message:
    role: str          # "system" | "user" | "assistant" | "tool"
    content: str
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    tool_call_id: str | None = None
    name: str | None = None

    def to_dict(self) -> dict:
        d: dict = {"role": self.role, "content": self.content}
        if self.tool_call_id:
            d["tool_call_id"] = self.tool_call_id
        if self.name:
            d["name"] = self.name
        return d


class ShortTermMemory:
    """
    Sliding-window conversation buffer.

    The buffer always starts with the system message (index 0).
    When the total token count exceeds the budget, the oldest non-system
    messages are dropped in pairs (user + assistant) to preserve coherence.
    """

    def __init__(self, token_budget: int | None = None) -> None:
        self.token_budget = (token_budget or settings.max_context_tokens) - OUTPUT_TOKEN_BUDGET
        self._messages: list[Message] = []

    # ── Public interface ──────────────────────────────────────────────────────

    def set_system(self, content: str) -> None:
        """Set or replace the system prompt. Always stays at index 0."""
        system_msg = Message(role="system", content=content)
        if self._messages and self._messages[0].role == "system":
            self._messages[0] = system_msg
        else:
            self._messages.insert(0, system_msg)

    def add(self, role: str, content: str, **kwargs) -> None:
        """Append a message and trim if necessary."""
        self._messages.append(Message(role=role, content=content, **kwargs))
        self._trim()

    def add_user(self, content: str) -> None:
        self.add("user", content)

    def add_assistant(self, content: str) -> None:
        self.add("assistant", content)

    def add_tool_result(self, tool_call_id: str, name: str, content: str) -> None:
        self.add("tool", content, tool_call_id=tool_call_id, name=name)

    def get_messages(self) -> list[dict]:
        """Return messages in the format litellm / OpenAI expects."""
        return [m.to_dict() for m in self._messages]

    def clear(self, keep_system: bool = True) -> None:
        """Reset the buffer, optionally preserving the system prompt."""
        if keep_system and self._messages and self._messages[0].role == "system":
            system = self._messages[0]
            self._messages = [system]
        else:
            self._messages = []

    @property
    def message_count(self) -> int:
        return len(self._messages)

    @property
    def token_count(self) -> int:
        full_text = " ".join(m.content for m in self._messages)
        return llm_client.count_tokens(full_text)

    # ── Internal ──────────────────────────────────────────────────────────────

    def _trim(self) -> None:
        """Drop oldest non-system messages until we're within budget."""
        while self.token_count > self.token_budget and len(self._messages) > 2:
            # Find the first non-system message and remove it
            for i, msg in enumerate(self._messages):
                if msg.role != "system":
                    removed = self._messages.pop(i)
                    logger.debug(
                        "short_term_trim",
                        removed_role=removed.role,
                        remaining=len(self._messages),
                    )
                    break
            else:
                break  # Only system message left, can't trim further
