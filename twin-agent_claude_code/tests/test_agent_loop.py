"""
tests/test_agent_loop.py

Tests for the agent's ReAct loop — LLM is mocked so these run instantly
with zero API calls and no keys needed.

Run with:
    pytest tests/test_agent_loop.py -v
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import tempfile
import os


@pytest.fixture
def temp_dirs(tmp_path):
    """Set up temp directories for memory during tests."""
    os.environ["DATABASE_URL"] = f"sqlite:///{tmp_path}/test.db"
    os.environ["CHROMA_PERSIST_PATH"] = str(tmp_path / "chroma")
    return tmp_path


@pytest.fixture
def mock_registry():
    """Registry with one fake tool."""
    from integrations.base import BaseTool, ToolRegistry

    class FakeTool(BaseTool):
        name = "fake_tool"
        description = "A fake tool for testing"
        parameters = {
            "type": "object",
            "properties": {
                "input": {"type": "string"}
            },
            "required": ["input"],
        }

        async def run(self, input: str = "", **kwargs) -> str:
            return f"Fake result for: {input}"

    registry = ToolRegistry()
    registry.register(FakeTool())
    return registry


@pytest.fixture
def memories(temp_dirs):
    from memory.episodic import EpisodicMemory
    from memory.semantic import SemanticMemory
    return EpisodicMemory(), SemanticMemory()


class TestReActParsing:
    """Test the action parsing logic without running the full loop."""

    def setup_method(self):
        from agent.core import TwinAgent
        from integrations.base import ToolRegistry
        from memory.episodic import EpisodicMemory
        from memory.semantic import SemanticMemory
        import tempfile, os

        tmp = tempfile.mkdtemp()
        os.environ["DATABASE_URL"] = f"sqlite:///{tmp}/test.db"
        os.environ["CHROMA_PERSIST_PATH"] = f"{tmp}/chroma"

        self.agent = TwinAgent(
            registry=ToolRegistry(),
            episodic=EpisodicMemory(),
            semantic=SemanticMemory(),
        )

    def test_parse_valid_action(self):
        response = """Thought: I should search the web for this.
Action: browser_search_web
Action Input: {"query": "AI agent frameworks 2024"}"""
        action, input_dict = self.agent._parse_action(response)
        assert action == "browser_search_web"
        assert input_dict["query"] == "AI agent frameworks 2024"

    def test_parse_no_action(self):
        response = "Thought: I need to think about this more."
        action, input_dict = self.agent._parse_action(response)
        assert action == ""
        assert input_dict == {}

    def test_extract_final_answer(self):
        response = """Thought: I have enough information.
Final Answer: Here is the summary of your emails: ..."""
        answer = self.agent._extract_final_answer(response)
        assert answer.startswith("Here is the summary")

    def test_extract_final_answer_multiline(self):
        response = """Thought: Done.
Final Answer: Line one.
Line two.
Line three."""
        answer = self.agent._extract_final_answer(response)
        assert "Line one" in answer
        assert "Line two" in answer


class TestAgentRun:
    """Test the full run loop with a mocked LLM."""

    @pytest.mark.asyncio
    async def test_run_reaches_final_answer(self, mock_registry, memories):
        """Agent should stop when LLM outputs Final Answer."""
        from agent.core import TwinAgent

        episodic, semantic = memories
        agent = TwinAgent(registry=mock_registry, episodic=episodic, semantic=semantic)

        # Mock the LLM to immediately return a Final Answer
        agent.llm = AsyncMock()
        agent.llm.chat_text = AsyncMock(return_value="Thought: Done.\nFinal Answer: Task complete.")
        agent.llm.count_tokens = MagicMock(return_value=10)

        result = await agent.run("Do something simple")

        assert result.success is True
        assert "Task complete" in result.answer
        assert result.iterations == 1

    @pytest.mark.asyncio
    async def test_run_uses_tool_then_answers(self, mock_registry, memories):
        """Agent should call a tool, get an observation, then answer."""
        from agent.core import TwinAgent

        episodic, semantic = memories
        agent = TwinAgent(registry=mock_registry, episodic=episodic, semantic=semantic)

        responses = iter([
            # First call: use the tool
            'Thought: I should use fake_tool.\nAction: fake_tool\nAction Input: {"input": "hello"}',
            # Second call: final answer after seeing observation
            "Thought: Got the result.\nFinal Answer: The tool returned a result.",
        ])

        agent.llm = AsyncMock()
        agent.llm.chat_text = AsyncMock(side_effect=lambda **_: next(responses))
        agent.llm.count_tokens = MagicMock(return_value=10)

        result = await agent.run("Use the fake tool")

        assert result.success is True
        assert result.iterations == 2

        action_events = [e for e in result.events if e["type"] == "action"]
        assert len(action_events) == 1
        assert action_events[0]["tool"] == "fake_tool"

    @pytest.mark.asyncio
    async def test_run_handles_unknown_tool(self, mock_registry, memories):
        """Agent should recover gracefully when it calls a non-existent tool."""
        from agent.core import TwinAgent

        episodic, semantic = memories
        agent = TwinAgent(registry=mock_registry, episodic=episodic, semantic=semantic)

        responses = iter([
            'Thought: I will use nonexistent_tool.\nAction: nonexistent_tool\nAction Input: {"x": 1}',
            "Thought: The tool failed but I can still answer.\nFinal Answer: Could not use that tool.",
        ])

        agent.llm = AsyncMock()
        agent.llm.chat_text = AsyncMock(side_effect=lambda **_: next(responses))
        agent.llm.count_tokens = MagicMock(return_value=10)

        result = await agent.run("Try a missing tool")

        # Should succeed despite tool error — agent recovered
        assert result.success is True

    @pytest.mark.asyncio
    async def test_session_id_generated(self, mock_registry, memories):
        from agent.core import TwinAgent

        episodic, semantic = memories
        agent = TwinAgent(registry=mock_registry, episodic=episodic, semantic=semantic)
        agent.llm = AsyncMock()
        agent.llm.chat_text = AsyncMock(return_value="Final Answer: Done.")
        agent.llm.count_tokens = MagicMock(return_value=10)

        result = await agent.run("Test task")

        assert result.session_id is not None
        assert len(result.session_id) > 0

    @pytest.mark.asyncio
    async def test_custom_session_id_preserved(self, mock_registry, memories):
        from agent.core import TwinAgent

        episodic, semantic = memories
        agent = TwinAgent(registry=mock_registry, episodic=episodic, semantic=semantic)
        agent.llm = AsyncMock()
        agent.llm.chat_text = AsyncMock(return_value="Final Answer: Done.")
        agent.llm.count_tokens = MagicMock(return_value=10)

        result = await agent.run("Test task", session_id="my-custom-session")

        assert result.session_id == "my-custom-session"
