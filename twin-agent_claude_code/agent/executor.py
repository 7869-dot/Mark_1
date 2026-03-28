"""
agent/executor.py

Wires everything together — builds the ToolRegistry and TwinAgent,
ready to be used by the API, CLI, or tests.

This is the single place where all integrations are registered.
Adding a new tool = import it here + call registry.register().
"""

from __future__ import annotations

from config.logging import get_logger, setup_logging
from config.settings import settings
from integrations.base import ToolRegistry
from integrations.browser import BrowserFetchPage, BrowserSearchWeb
from integrations.gmail import GmailReadInbox, GmailSearch, GmailSendEmail
from integrations.slack import SlackListChannels, SlackReadChannel, SlackSendMessage
from integrations.twitter import TwitterPostTweet, TwitterReadTimeline, TwitterSearch
from memory.episodic import EpisodicMemory
from memory.semantic import SemanticMemory

logger = get_logger(__name__)


def build_registry() -> ToolRegistry:
    """
    Create and populate the ToolRegistry with all available tools.

    Tools that aren't configured (missing API keys) are skipped automatically
    via BaseTool.is_available() — no errors, just not registered.
    """
    registry = ToolRegistry()

    # Gmail
    registry.register(GmailReadInbox())
    registry.register(GmailSendEmail())
    registry.register(GmailSearch())

    # Slack
    registry.register(SlackSendMessage())
    registry.register(SlackReadChannel())
    registry.register(SlackListChannels())

    # Twitter / X
    registry.register(TwitterPostTweet())
    registry.register(TwitterReadTimeline())
    registry.register(TwitterSearch())

    # Browser (always available — no API key needed)
    registry.register(BrowserFetchPage())
    registry.register(BrowserSearchWeb())

    logger.info("registry_built", tool_count=len(registry))

    if len(registry) == 0:
        logger.warning(
            "no_tools_registered",
            hint="Check your .env — no API keys found for any integration.",
        )
    else:
        tool_names = [t.name for t in registry.all()]
        logger.info("tools_available", tools=tool_names)

    return registry


def build_agent():
    """
    Build a fully wired TwinAgent instance.
    Call this once at startup and reuse the instance.
    """
    from agent.core import TwinAgent

    setup_logging()

    registry = build_registry()
    episodic = EpisodicMemory()
    semantic = SemanticMemory()

    agent = TwinAgent(
        registry=registry,
        episodic=episodic,
        semantic=semantic,
    )

    logger.info(
        "agent_ready",
        name=settings.agent_name,
        model=settings.llm_model,
        tools=len(registry),
    )

    return agent
