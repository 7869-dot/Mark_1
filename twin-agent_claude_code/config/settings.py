"""
config/settings.py

Single source of truth for all configuration.
Pydantic validates every value at startup — if a required key is missing,
the app crashes immediately with a clear error instead of failing silently later.
"""

from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ── LLM ──────────────────────────────────────────────────────────────────
    openai_api_key: str = ""
    anthropic_api_key: str = ""
    llm_model: str = "gpt-4o"
    llm_temperature: float = 0.2
    llm_max_tokens: int = 4096

    # ── Agent ─────────────────────────────────────────────────────────────────
    agent_name: str = "twin"
    persona_description: str = "A highly capable AI assistant acting on behalf of its owner."
    max_agent_iterations: int = 15
    max_context_tokens: int = 120000

    # ── Memory ────────────────────────────────────────────────────────────────
    database_url: str = "sqlite:///./data/agent_memory.db"
    chroma_persist_path: str = "./data/chroma_db"
    embedding_model: str = "all-MiniLM-L6-v2"

    # ── Gmail ─────────────────────────────────────────────────────────────────
    gmail_client_id: str = ""
    gmail_client_secret: str = ""
    gmail_redirect_uri: str = "http://localhost:8000/auth/gmail/callback"
    gmail_token_path: str = "./data/gmail_token.json"

    # ── Slack ─────────────────────────────────────────────────────────────────
    slack_bot_token: str = ""
    slack_signing_secret: str = ""

    # ── Twitter ───────────────────────────────────────────────────────────────
    twitter_api_key: str = ""
    twitter_api_secret: str = ""
    twitter_access_token: str = ""
    twitter_access_token_secret: str = ""
    twitter_bearer_token: str = ""

    # ── API server ────────────────────────────────────────────────────────────
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_secret_key: str = "change-this-to-a-random-string"
    debug: bool = True

    @property
    def has_openai(self) -> bool:
        return bool(self.openai_api_key and self.openai_api_key.startswith("sk-"))

    @property
    def has_anthropic(self) -> bool:
        return bool(self.anthropic_api_key and self.anthropic_api_key.startswith("sk-ant-"))

    @property
    def has_gmail(self) -> bool:
        return bool(self.gmail_client_id and self.gmail_client_secret)

    @property
    def has_slack(self) -> bool:
        return bool(self.slack_bot_token)

    @property
    def has_twitter(self) -> bool:
        return bool(self.twitter_api_key and self.twitter_bearer_token)


@lru_cache
def get_settings() -> Settings:
    """Return a cached singleton Settings instance."""
    return Settings()


# Convenience alias used everywhere else in the codebase
settings = get_settings()
