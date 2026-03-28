"""
integrations/slack.py

Slack integration — three tools:
  - slack_send_message:   post to a channel or DM
  - slack_read_channel:   fetch recent messages from a channel
  - slack_list_channels:  list available channels
"""

from __future__ import annotations

from typing import Any

from config.logging import get_logger
from config.settings import settings
from integrations.base import BaseTool, ToolError

logger = get_logger(__name__)


def _get_slack_client():
    try:
        from slack_sdk import WebClient
        return WebClient(token=settings.slack_bot_token)
    except ImportError:
        raise ToolError("slack-sdk not installed. Run: pip install slack-sdk")


class SlackSendMessage(BaseTool):
    name = "slack_send_message"
    description = "Send a message to a Slack channel or direct message. Channel names start with #, DMs use @username."
    parameters = {
        "type": "object",
        "properties": {
            "channel": {"type": "string", "description": "Channel name (e.g. '#general') or user ID for DM"},
            "message": {"type": "string", "description": "Message text to send"},
            "thread_ts": {"type": "string", "description": "Timestamp of parent message to reply in thread (optional)"},
        },
        "required": ["channel", "message"],
    }

    def is_available(self) -> bool:
        return settings.has_slack

    async def run(self, channel: str, message: str, thread_ts: str = "", **kwargs) -> str:
        try:
            client = _get_slack_client()
            params: dict[str, Any] = {"channel": channel, "text": message}
            if thread_ts:
                params["thread_ts"] = thread_ts

            response = client.chat_postMessage(**params)
            if response["ok"]:
                logger.info("slack_sent", channel=channel)
                return f"Message sent to {channel}"
            else:
                raise ToolError(f"Slack API error: {response.get('error', 'unknown')}")

        except ToolError:
            raise
        except Exception as e:
            raise ToolError(f"Failed to send Slack message: {e}")


class SlackReadChannel(BaseTool):
    name = "slack_read_channel"
    description = "Read recent messages from a Slack channel."
    parameters = {
        "type": "object",
        "properties": {
            "channel": {"type": "string", "description": "Channel ID or name (e.g. 'C12345' or '#general')"},
            "limit": {"type": "integer", "description": "Number of messages to fetch (1-20, default 10)", "default": 10},
        },
        "required": ["channel"],
    }

    def is_available(self) -> bool:
        return settings.has_slack

    async def run(self, channel: str, limit: int = 10, **kwargs) -> str:
        try:
            client = _get_slack_client()
            response = client.conversations_history(channel=channel, limit=min(limit, 20))

            if not response["ok"]:
                raise ToolError(f"Slack error: {response.get('error', 'unknown')}")

            messages = response.get("messages", [])
            if not messages:
                return f"No messages found in {channel}"

            lines = []
            for msg in reversed(messages):
                user = msg.get("user", "bot")
                text = msg.get("text", "")[:200]
                lines.append(f"[{user}]: {text}")

            return f"Messages from {channel}:\n" + "\n".join(lines)

        except ToolError:
            raise
        except Exception as e:
            raise ToolError(f"Failed to read Slack channel: {e}")


class SlackListChannels(BaseTool):
    name = "slack_list_channels"
    description = "List available Slack channels the bot has access to."
    parameters = {
        "type": "object",
        "properties": {
            "limit": {"type": "integer", "description": "Max channels to list", "default": 20},
        },
        "required": [],
    }

    def is_available(self) -> bool:
        return settings.has_slack

    async def run(self, limit: int = 20, **kwargs) -> str:
        try:
            client = _get_slack_client()
            response = client.conversations_list(limit=min(limit, 100))

            if not response["ok"]:
                raise ToolError(f"Slack error: {response.get('error', 'unknown')}")

            channels = response.get("channels", [])
            if not channels:
                return "No channels found."

            lines = [f"#{ch['name']} (ID: {ch['id']})" for ch in channels]
            return f"Available channels:\n" + "\n".join(lines)

        except ToolError:
            raise
        except Exception as e:
            raise ToolError(f"Failed to list channels: {e}")
