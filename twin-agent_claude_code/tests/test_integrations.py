"""
tests/test_integrations.py

Tests for the integration layer.
These test the tool interface and error handling — not the actual API calls.

Run with:
    pytest tests/test_integrations.py -v
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch


class TestBaseTool:
    def test_schema_shape(self):
        from integrations.base import BaseTool

        class MyTool(BaseTool):
            name = "my_tool"
            description = "Does something"
            parameters = {"type": "object", "properties": {}, "required": []}

            async def run(self, **kwargs):
                return "result"

        tool = MyTool()
        schema = tool.schema

        assert schema["type"] == "function"
        assert schema["function"]["name"] == "my_tool"
        assert schema["function"]["description"] == "Does something"
        assert "parameters" in schema["function"]

    def test_is_available_default_true(self):
        from integrations.base import BaseTool

        class AlwaysOnTool(BaseTool):
            name = "always_on"
            description = "Always available"
            parameters = {"type": "object", "properties": {}}

            async def run(self, **kwargs):
                return "ok"

        assert AlwaysOnTool().is_available() is True


class TestToolRegistry:
    def setup_method(self):
        from integrations.base import BaseTool, ToolRegistry

        class ToolA(BaseTool):
            name = "tool_a"
            description = "Tool A"
            parameters = {}
            async def run(self, **kwargs): return "a"

        class ToolB(BaseTool):
            name = "tool_b"
            description = "Tool B"
            parameters = {}
            async def run(self, **kwargs): return "b"

        class UnavailableTool(BaseTool):
            name = "unavailable"
            description = "Not available"
            parameters = {}
            def is_available(self): return False
            async def run(self, **kwargs): return "nope"

        self.registry = ToolRegistry()
        self.registry.register(ToolA())
        self.registry.register(ToolB())
        self.registry.register(UnavailableTool())

    def test_unavailable_tools_skipped(self):
        assert len(self.registry) == 2
        tool_names = [t.name for t in self.registry.all()]
        assert "unavailable" not in tool_names

    def test_get_existing_tool(self):
        tool = self.registry.get("tool_a")
        assert tool.name == "tool_a"

    def test_get_missing_tool_raises(self):
        from integrations.base import ToolError
        with pytest.raises(ToolError):
            self.registry.get("nonexistent")

    def test_schemas_returns_list(self):
        schemas = self.registry.schemas()
        assert len(schemas) == 2
        assert all("function" in s for s in schemas)

    def test_descriptions_returns_string(self):
        desc = self.registry.descriptions()
        assert "tool_a" in desc
        assert "tool_b" in desc


class TestGmailToolAvailability:
    def test_unavailable_without_credentials(self, monkeypatch):
        monkeypatch.setenv("GMAIL_CLIENT_ID", "")
        monkeypatch.setenv("GMAIL_CLIENT_SECRET", "")

        # Force settings reload
        import importlib
        import config.settings as cs
        cs._settings_cache = None

        from integrations.gmail import GmailReadInbox
        tool = GmailReadInbox()
        assert tool.is_available() is False


class TestBrowserTool:
    @pytest.mark.asyncio
    async def test_invalid_url_raises_tool_error(self):
        from integrations.base import ToolError
        from integrations.browser import BrowserFetchPage

        tool = BrowserFetchPage()
        with pytest.raises(ToolError, match="Invalid URL"):
            await tool.run(url="not-a-url")

    def test_browser_always_available(self):
        from integrations.browser import BrowserFetchPage, BrowserSearchWeb
        assert BrowserFetchPage().is_available() is True
        assert BrowserSearchWeb().is_available() is True
