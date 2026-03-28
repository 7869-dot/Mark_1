"""
tests/test_memory.py

Tests for the memory system — short-term, episodic, and semantic.
These run locally with no LLM calls and no API keys needed.

Run with:
    pytest tests/test_memory.py -v
"""

import pytest
import tempfile
import os


# ── Short-term memory ─────────────────────────────────────────────────────────

class TestShortTermMemory:
    def setup_method(self):
        from memory.short_term import ShortTermMemory
        self.mem = ShortTermMemory(token_budget=10000)

    def test_set_system(self):
        self.mem.set_system("You are a helpful agent.")
        messages = self.mem.get_messages()
        assert len(messages) == 1
        assert messages[0]["role"] == "system"
        assert messages[0]["content"] == "You are a helpful agent."

    def test_replace_system(self):
        self.mem.set_system("First system prompt")
        self.mem.set_system("Second system prompt")
        messages = self.mem.get_messages()
        assert len(messages) == 1
        assert messages[0]["content"] == "Second system prompt"

    def test_add_messages(self):
        self.mem.set_system("System")
        self.mem.add_user("Hello")
        self.mem.add_assistant("Hi there!")
        messages = self.mem.get_messages()
        assert len(messages) == 3
        assert messages[1]["role"] == "user"
        assert messages[2]["role"] == "assistant"

    def test_clear_keeps_system(self):
        self.mem.set_system("System prompt")
        self.mem.add_user("Some message")
        self.mem.add_assistant("Some response")
        self.mem.clear(keep_system=True)
        messages = self.mem.get_messages()
        assert len(messages) == 1
        assert messages[0]["role"] == "system"

    def test_clear_removes_system(self):
        self.mem.set_system("System prompt")
        self.mem.add_user("Some message")
        self.mem.clear(keep_system=False)
        messages = self.mem.get_messages()
        assert len(messages) == 0

    def test_message_count(self):
        self.mem.set_system("S")
        self.mem.add_user("U")
        self.mem.add_assistant("A")
        assert self.mem.message_count == 3


# ── Episodic memory ───────────────────────────────────────────────────────────

class TestEpisodicMemory:
    def setup_method(self):
        # Use an in-memory SQLite database for tests
        import os
        os.environ["DATABASE_URL"] = "sqlite:///:memory:"
        from memory.episodic import EpisodicMemory, EventType
        self.mem = EpisodicMemory()
        self.EventType = EventType

    def test_log_event(self):
        event = self.mem.log(
            session_id="test-session",
            event_type=self.EventType.TASK_START,
            content="Test task",
        )
        assert event.id is not None
        assert event.session_id == "test-session"
        assert event.event_type == "task_start"
        assert event.content == "Test task"

    def test_get_session(self):
        self.mem.log("session-1", self.EventType.TASK_START, "Task A")
        self.mem.log("session-1", self.EventType.ACTION, "Called gmail")
        self.mem.log("session-2", self.EventType.TASK_START, "Task B")

        events = self.mem.get_session("session-1")
        assert len(events) == 2
        assert all(e.session_id == "session-1" for e in events)

    def test_get_recent(self):
        for i in range(5):
            self.mem.log(f"session-{i}", self.EventType.TASK_START, f"Task {i}")

        recent = self.mem.get_recent(limit=3)
        assert len(recent) == 3

    def test_metadata_stored(self):
        self.mem.log(
            "session-1",
            self.EventType.ACTION,
            "Called tool",
            metadata={"tool": "gmail", "args": {"to": "test@example.com"}},
        )
        events = self.mem.get_session("session-1")
        assert events[0].metadata["tool"] == "gmail"

    def test_format_session(self):
        self.mem.log("session-1", self.EventType.TASK_START, "Read emails")
        self.mem.log("session-1", self.EventType.TASK_COMPLETE, "Found 3 emails")

        formatted = self.mem.format_session_for_context("session-1")
        assert "session-1" in formatted
        assert "TASK_START" in formatted.upper() or "task_start" in formatted


# ── Semantic memory ───────────────────────────────────────────────────────────

class TestSemanticMemory:
    def setup_method(self):
        self.tmpdir = tempfile.mkdtemp()
        import os
        os.environ["CHROMA_PERSIST_PATH"] = self.tmpdir
        from memory.semantic import SemanticMemory
        self.mem = SemanticMemory()

    def test_store_and_count(self):
        assert self.mem.count() == 0
        self.mem.store("The agent prefers short emails.")
        assert self.mem.count() == 1

    def test_store_returns_id(self):
        doc_id = self.mem.store("Test memory entry")
        assert isinstance(doc_id, str)
        assert len(doc_id) > 0

    def test_stable_id_upsert(self):
        self.mem.store("Original text", doc_id="stable-id")
        self.mem.store("Updated text", doc_id="stable-id")
        assert self.mem.count() == 1  # Upsert, not insert

    def test_search_returns_results(self):
        self.mem.store("The user prefers morning meetings.")
        self.mem.store("Always write concise emails.")
        self.mem.store("The user is building an AI startup.")

        results = self.mem.search("meeting schedule preferences", n_results=2)
        assert len(results) > 0
        assert "text" in results[0]
        assert "distance" in results[0]

    def test_search_empty_store(self):
        results = self.mem.search("anything")
        assert results == []

    def test_delete(self):
        doc_id = self.mem.store("To be deleted")
        assert self.mem.count() == 1
        self.mem.delete(doc_id)
        assert self.mem.count() == 0

    def test_empty_text_raises(self):
        with pytest.raises(ValueError):
            self.mem.store("   ")

    def test_format_for_prompt(self):
        self.mem.store("User prefers direct communication.")
        self.mem.store("User is an engineer at a startup.")

        context = self.mem.format_for_prompt("communication style")
        # Should return non-empty string with relevant content
        assert isinstance(context, str)
