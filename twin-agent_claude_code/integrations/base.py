"""
integrations/base.py

Abstract base class for all integrations (tools).

Every tool the agent can use follows this interface.
The agent sees a list of BaseTool instances and calls tool.run(input).
Adding a new integration = create a new file + subclass BaseTool.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class BaseTool(ABC):
    """
    Every integration must implement this interface.

    The `schema` property tells the LLM what the tool does and what arguments
    it accepts. This is passed directly to the LLM as a function definition.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Unique tool name — used by the agent to call this tool."""
        ...

    @property
    @abstractmethod
    def description(self) -> str:
        """
        What this tool does, written for the LLM.
        Be specific — the LLM decides which tool to use based on this.
        """
        ...

    @property
    @abstractmethod
    def parameters(self) -> dict[str, Any]:
        """
        JSON Schema describing the tool's input parameters.
        Follows OpenAI function calling format.
        """
        ...

    @abstractmethod
    async def run(self, **kwargs: Any) -> str:
        """
        Execute the tool with the given arguments.
        Must return a string — this becomes the Observation in the ReAct loop.
        Raise ToolError for expected failures (auth, not found, rate limit).
        Raise exception for unexpected failures.
        """
        ...

    @property
    def schema(self) -> dict[str, Any]:
        """
        OpenAI-compatible function schema.
        Passed to the LLM as part of the tools list.
        """
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters,
            },
        }

    def is_available(self) -> bool:
        """
        Return True if this tool is configured and ready to use.
        Override to check API keys or credentials.
        """
        return True

    def __repr__(self) -> str:
        return f"<Tool: {self.name}>"


class ToolError(Exception):
    """Raised when a tool encounters an expected failure (auth, rate limit, not found)."""
    pass


class ToolRegistry:
    """
    Holds all available tools and provides lookup by name.

    Usage:
        registry = ToolRegistry()
        registry.register(GmailTool())
        registry.register(SlackTool())

        tool = registry.get("gmail_send_email")
        result = await tool.run(to="...", subject="...", body="...")
    """

    def __init__(self) -> None:
        self._tools: dict[str, BaseTool] = {}

    def register(self, tool: BaseTool) -> None:
        if not tool.is_available():
            return  # Skip tools that aren't configured
        self._tools[tool.name] = tool

    def get(self, name: str) -> BaseTool:
        if name not in self._tools:
            raise ToolError(f"Tool '{name}' not found. Available: {list(self._tools.keys())}")
        return self._tools[name]

    def all(self) -> list[BaseTool]:
        return list(self._tools.values())

    def schemas(self) -> list[dict[str, Any]]:
        """Return all tool schemas for passing to the LLM."""
        return [tool.schema for tool in self._tools.values()]

    def descriptions(self) -> str:
        """Return a human-readable list of tools for system prompts."""
        lines = []
        for tool in self._tools.values():
            lines.append(f"- {tool.name}: {tool.description}")
        return "\n".join(lines)

    def __len__(self) -> int:
        return len(self._tools)
