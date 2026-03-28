"""
agent/persona.py

Persona management — builds the identity layer that makes the agent feel like
a specific person rather than a generic assistant.

In v0.1 this is loaded from .env and a JSON file.
In v1.0 this will be built from the user's actual communication data.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from typing import Any

from config.logging import get_logger
from config.settings import settings

logger = get_logger(__name__)

PERSONA_FILE = "./data/persona.json"


@dataclass
class Persona:
    name: str
    description: str
    communication_style: str = "Clear, direct, and professional."
    values: list[str] = field(default_factory=list)
    preferences: dict[str, Any] = field(default_factory=dict)
    background: str = ""

    def to_prompt_block(self) -> str:
        """
        Render the persona as a prompt block injected into the system message.
        The more specific this is, the more the agent acts like a real person.
        """
        lines = [
            f"You are acting as {self.name}.",
            f"{self.description}",
        ]

        if self.background:
            lines.append(f"\nBackground: {self.background}")

        if self.communication_style:
            lines.append(f"\nCommunication style: {self.communication_style}")

        if self.values:
            lines.append(f"\nCore values: {', '.join(self.values)}")

        if self.preferences:
            prefs = "\n".join(f"  - {k}: {v}" for k, v in self.preferences.items())
            lines.append(f"\nPreferences:\n{prefs}")

        lines.append(
            "\nAlways make decisions and communicate in a way that reflects "
            "this person's identity. You are not a generic assistant — "
            "you are their digital twin."
        )

        return "\n".join(lines)


def load_persona() -> Persona:
    """
    Load persona from persona.json if it exists, otherwise fall back to settings.

    The JSON file is the richer source — it can hold communication style,
    values, preferences, and background that .env can't easily express.
    """
    if os.path.exists(PERSONA_FILE):
        try:
            with open(PERSONA_FILE) as f:
                data = json.load(f)
            persona = Persona(
                name=data.get("name", settings.agent_name),
                description=data.get("description", settings.persona_description),
                communication_style=data.get("communication_style", "Clear and direct."),
                values=data.get("values", []),
                preferences=data.get("preferences", {}),
                background=data.get("background", ""),
            )
            logger.info("persona_loaded", source="file", name=persona.name)
            return persona
        except Exception as e:
            logger.warning("persona_file_load_failed", error=str(e))

    # Fallback: build from .env settings
    persona = Persona(
        name=settings.agent_name,
        description=settings.persona_description,
    )
    logger.info("persona_loaded", source="settings", name=persona.name)
    return persona


def create_default_persona_file() -> None:
    """
    Write a starter persona.json to ./data/.
    Edit this file to customize how the agent represents you.
    """
    os.makedirs("./data", exist_ok=True)

    default = {
        "name": "Alex",
        "description": (
            "A driven, thoughtful professional who values clarity, speed, and "
            "getting things done properly. Hates unnecessary back-and-forth. "
            "Prefers to over-communicate context upfront so meetings and emails "
            "don't spiral into clarification threads."
        ),
        "background": (
            "Engineer turned founder. Technical background means I can go deep "
            "on implementation details when needed, but I always tie things back "
            "to user impact and business outcomes."
        ),
        "communication_style": (
            "Direct and concise. Bullet points for lists. "
            "Short paragraphs. No filler phrases like 'Hope this finds you well'. "
            "Friendly but efficient. Signs off as 'Alex'."
        ),
        "values": [
            "Speed with quality",
            "Honest feedback over comfortable silence",
            "Systems thinking",
            "Respecting people's time",
        ],
        "preferences": {
            "email_tone": "professional but warm",
            "email_length": "short — under 150 words unless complex topic",
            "meeting_scheduling": "prefer mornings, avoid Fridays",
            "slack_style": "no hello messages, lead with the ask",
            "twitter_voice": "thoughtful takes on AI, startups, and engineering",
        },
    }

    with open(PERSONA_FILE, "w") as f:
        json.dump(default, f, indent=2)

    logger.info("persona_file_created", path=PERSONA_FILE)
    print(f"Created persona file at {PERSONA_FILE} — edit it to customize the agent.")


# Module-level singleton
persona = load_persona()
