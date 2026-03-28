"""
llm/client.py

Thin wrapper around litellm so the rest of the codebase never imports
openai or anthropic directly. Swap models by changing LLM_MODEL in .env.

litellm speaks to OpenAI, Anthropic, Groq, and local models with
the same interface — one change in config, zero code changes everywhere else.
"""

from __future__ import annotations

import os
from typing import Any

import litellm
from tenacity import retry, stop_after_attempt, wait_exponential

from config.logging import get_logger
from config.settings import settings

logger = get_logger(__name__)

# Point litellm at our keys
os.environ["OPENAI_API_KEY"] = settings.openai_api_key
os.environ["ANTHROPIC_API_KEY"] = settings.anthropic_api_key

# Silence litellm's own verbose logging unless we're debugging
litellm.set_verbose = settings.debug


class LLMClient:
    """
    Async LLM client.

    Usage:
        client = LLMClient()
        response = await client.chat(messages=[{"role": "user", "content": "hello"}])
    """

    def __init__(
        self,
        model: str | None = None,
        temperature: float | None = None,
        max_tokens: int | None = None,
    ) -> None:
        self.model = model or settings.llm_model
        self.temperature = temperature if temperature is not None else settings.llm_temperature
        self.max_tokens = max_tokens or settings.llm_max_tokens

        logger.info("llm_client_init", model=self.model, temperature=self.temperature)

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        reraise=True,
    )
    async def chat(
        self,
        messages: list[dict[str, str]],
        tools: list[dict[str, Any]] | None = None,
        tool_choice: str | dict | None = None,
        **kwargs: Any,
    ) -> litellm.ModelResponse:
        """
        Send a chat completion request.

        Args:
            messages: OpenAI-format message list
            tools:    Optional list of tool schemas (function calling)
            tool_choice: "auto" | "required" | specific tool
            **kwargs: Passed directly to litellm.acompletion

        Returns:
            litellm ModelResponse — same shape as OpenAI's response object
        """
        params: dict[str, Any] = {
            "model": self.model,
            "messages": messages,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            **kwargs,
        }

        if tools:
            params["tools"] = tools
            params["tool_choice"] = tool_choice or "auto"

        logger.debug(
            "llm_request",
            model=self.model,
            message_count=len(messages),
            has_tools=bool(tools),
        )

        response = await litellm.acompletion(**params)

        logger.debug(
            "llm_response",
            model=self.model,
            finish_reason=response.choices[0].finish_reason,
            usage=response.usage.model_dump() if response.usage else None,
        )

        return response

    async def chat_text(self, messages: list[dict[str, str]], **kwargs: Any) -> str:
        """Convenience wrapper that returns just the text content of the response."""
        response = await self.chat(messages, **kwargs)
        return response.choices[0].message.content or ""

    def count_tokens(self, text: str) -> int:
        """Estimate token count for a string using litellm's tokenizer."""
        try:
            return litellm.token_counter(model=self.model, text=text)
        except Exception:
            # Rough fallback: 1 token ≈ 4 chars
            return len(text) // 4


# Module-level singleton — import this everywhere
llm_client = LLMClient()
