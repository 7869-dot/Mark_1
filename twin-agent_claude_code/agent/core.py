"""
agent/core.py

The agent's brain — the ReAct (Reason + Act) loop.

Flow for every task:
  1. Build system prompt (persona + tools + memory context)
  2. Loop:
     a. Call LLM → get Thought + Action
     b. Parse which tool to call and with what args
     c. Execute the tool → get Observation
     d. Add Observation to context
     e. If LLM outputs "Final Answer" → done
  3. Log everything to episodic memory
  4. Consolidate session into semantic memory

This is intentionally straightforward — no magic, no hidden state.
Every step is logged so you can debug exactly what the agent was thinking.
"""

from __future__ import annotations

import json
import re
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

from config.logging import get_logger
from config.settings import settings
from integrations.base import ToolError, ToolRegistry
from llm.client import LLMClient
from llm.prompts import memory_summary_prompt, system_prompt, task_prompt
from memory.episodic import EpisodicMemory, EventType
from memory.retriever import MemoryRetriever
from memory.semantic import SemanticMemory
from memory.short_term import ShortTermMemory

logger = get_logger(__name__)


@dataclass
class AgentResult:
    """The result of running the agent on a task."""
    session_id: str
    task: str
    answer: str
    success: bool
    iterations: int
    duration_seconds: float
    events: list[dict] = field(default_factory=list)
    error: str | None = None


class TwinAgent:
    """
    Autonomous ReAct agent with memory and tool use.

    Usage:
        agent = TwinAgent(registry, episodic, semantic)
        result = await agent.run("Read my last 5 emails and summarize them")
        print(result.answer)
    """

    def __init__(
        self,
        registry: ToolRegistry,
        episodic: EpisodicMemory,
        semantic: SemanticMemory,
        llm: LLMClient | None = None,
    ) -> None:
        self.registry = registry
        self.episodic = episodic
        self.semantic = semantic
        self.retriever = MemoryRetriever(episodic, semantic)
        self.llm = llm or LLMClient()

    async def run(self, task: str, session_id: str | None = None) -> AgentResult:
        """
        Execute a task using the ReAct loop.

        Args:
            task:       Natural language task description
            session_id: Optional — pass to continue an existing session

        Returns:
            AgentResult with the final answer and full event log
        """
        session_id = session_id or str(uuid.uuid4())[:8]
        started_at = datetime.now(timezone.utc)
        events: list[dict] = []

        logger.info("agent_run_start", session_id=session_id, task=task[:100])

        # ── Log task start ────────────────────────────────────────────────────
        self.episodic.log(session_id, EventType.TASK_START, task)
        events.append({"type": "task_start", "content": task})

        # ── Retrieve memory context for this task ─────────────────────────────
        memory_context = self.retriever.get_context(task, current_session_id=session_id)
        if memory_context:
            self.episodic.log(session_id, EventType.MEMORY_RETRIEVED, memory_context[:200])

        # ── Build the conversation window ─────────────────────────────────────
        short_term = ShortTermMemory()
        short_term.set_system(
            system_prompt(
                tool_descriptions=self.registry.descriptions(),
                memory_context=memory_context,
            )
        )
        short_term.add_user(task_prompt(task))

        # ── ReAct loop ────────────────────────────────────────────────────────
        answer = ""
        final_answer = ""
        iteration = 0

        try:
            for iteration in range(1, settings.max_agent_iterations + 1):
                logger.debug("agent_iteration", session_id=session_id, iteration=iteration)

                # Call the LLM
                response_text = await self.llm.chat_text(
                    messages=short_term.get_messages()
                )

                # Add assistant response to context
                short_term.add_assistant(response_text)
                answer = response_text

                self.episodic.log(session_id, EventType.THOUGHT, response_text[:300])
                events.append({"type": "thought", "content": response_text, "iteration": iteration})

                # ── Check for Final Answer ────────────────────────────────────
                if "Final Answer:" in response_text:
                    final_answer = self._extract_final_answer(response_text)
                    logger.info(
                        "agent_complete",
                        session_id=session_id,
                        iterations=iteration,
                        answer_preview=final_answer[:100],
                    )
                    self.episodic.log(session_id, EventType.TASK_COMPLETE, final_answer)
                    break

                # ── Parse and execute tool call ───────────────────────────────
                action, action_input = self._parse_action(response_text)

                if not action:
                    # LLM didn't produce a valid action — nudge it
                    observation = "No valid Action found in your response. Please provide a Thought, Action, and Action Input, or output a Final Answer."
                else:
                    observation = await self._execute_action(
                        session_id, action, action_input, events
                    )

                # Add observation back to context
                obs_message = f"Observation: {observation}"
                short_term.add_user(obs_message)
                self.episodic.log(session_id, EventType.OBSERVATION, observation[:300])
                events.append({"type": "observation", "content": observation, "iteration": iteration})

            else:
                # Hit iteration limit
                final_answer = f"Task incomplete after {settings.max_agent_iterations} iterations. Last response: {answer[:200]}"
                self.episodic.log(session_id, EventType.TASK_FAILED, "Iteration limit reached")
                logger.warning("agent_iteration_limit", session_id=session_id)

        except Exception as e:
            final_answer = f"Agent encountered an error: {e}"
            self.episodic.log(session_id, EventType.TASK_FAILED, str(e))
            logger.error("agent_error", session_id=session_id, error=str(e), exc_info=True)

            duration = (datetime.now(timezone.utc) - started_at).total_seconds()
            return AgentResult(
                session_id=session_id,
                task=task,
                answer=final_answer,
                success=False,
                iterations=iteration,
                duration_seconds=duration,
                events=events,
                error=str(e),
            )

        # ── Consolidate session into semantic memory ───────────────────────────
        await self._consolidate(session_id, task, final_answer, events)

        duration = (datetime.now(timezone.utc) - started_at).total_seconds()
        logger.info(
            "agent_run_complete",
            session_id=session_id,
            duration=duration,
            iterations=iteration,
        )

        return AgentResult(
            session_id=session_id,
            task=task,
            answer=final_answer,
            success=True,
            iterations=iteration,
            duration_seconds=duration,
            events=events,
        )

    # ── Private helpers ───────────────────────────────────────────────────────

    def _parse_action(self, response: str) -> tuple[str, dict]:
        """
        Extract Action and Action Input from the LLM's response.

        Expected format:
            Action: tool_name
            Action Input: {"key": "value"}

        Returns (action_name, input_dict) or ("", {}) if not found.
        """
        action_match = re.search(r"Action:\s*(.+?)(?:\n|$)", response)
        input_match = re.search(r"Action Input:\s*(\{.+?\})", response, re.DOTALL)

        if not action_match:
            return "", {}

        action = action_match.group(1).strip()

        action_input: dict = {}
        if input_match:
            try:
                action_input = json.loads(input_match.group(1))
            except json.JSONDecodeError:
                # Try to extract a simpler string input
                raw = input_match.group(1).strip()
                action_input = {"input": raw}

        return action, action_input

    def _extract_final_answer(self, response: str) -> str:
        """Extract the text after 'Final Answer:' from the response."""
        match = re.search(r"Final Answer:\s*(.+)", response, re.DOTALL)
        return match.group(1).strip() if match else response.strip()

    async def _execute_action(
        self,
        session_id: str,
        action: str,
        action_input: dict,
        events: list,
    ) -> str:
        """Look up and execute a tool. Return the observation string."""
        logger.info(
            "agent_action",
            session_id=session_id,
            action=action,
            input_keys=list(action_input.keys()),
        )
        self.episodic.log(
            session_id,
            EventType.ACTION,
            f"{action}({json.dumps(action_input)[:200]})",
        )
        events.append({"type": "action", "tool": action, "input": action_input})

        try:
            tool = self.registry.get(action)
            result = await tool.run(**action_input)
            return result

        except ToolError as e:
            logger.warning("tool_error", action=action, error=str(e))
            return f"Tool error: {e}"
        except Exception as e:
            logger.error("tool_unexpected_error", action=action, error=str(e))
            return f"Unexpected error calling {action}: {e}"

    async def _consolidate(
        self,
        session_id: str,
        task: str,
        answer: str,
        events: list,
    ) -> None:
        """After a session, summarize and store it in semantic memory."""
        try:
            # Build a compact conversation summary for the LLM to compress
            tool_calls = [e for e in events if e["type"] == "action"]
            tools_used = [e["tool"] for e in tool_calls]

            summary_text = (
                f"Task: {task}\n"
                f"Tools used: {', '.join(tools_used) if tools_used else 'none'}\n"
                f"Outcome: {answer[:300]}"
            )

            # Ask the LLM to compress this into a memory entry
            compressed = await self.llm.chat_text(
                messages=[{"role": "user", "content": memory_summary_prompt(summary_text)}]
            )

            self.retriever.consolidate_session(
                session_id=session_id,
                summary=compressed,
                metadata={"task_preview": task[:80], "tools_used": ",".join(tools_used)},
            )

        except Exception as e:
            # Non-critical — don't let this fail the whole run
            logger.warning("consolidation_failed", session_id=session_id, error=str(e))
