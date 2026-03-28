"""
Seed a demo user, persona, and sample memories (requires DB + migrations).

Usage (from persona-ai/):
  pip install -e .
  set DATABASE_URL / export DATABASE_URL
  alembic upgrade head
  python scripts/seed_data.py
"""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.core.config import get_settings  # noqa: E402
from app.db.session import AsyncSessionLocal  # noqa: E402
from app.schemas.memory import MemoryIngest, MemorySourceType  # noqa: E402
from app.schemas.persona import PersonaCreate  # noqa: E402
from app.services.embedding_service import EmbeddingService  # noqa: E402
from app.services.memory_service import MemoryService  # noqa: E402
from app.services.persona_service import PersonaService  # noqa: E402
from app.services.user_service import UserService  # noqa: E402


async def main() -> None:
    get_settings()
    email = "seed@persona-ai.local"
    password = "seedpassword123"

    async with AsyncSessionLocal() as session:
        users = UserService(session)
        existing = await users.get_by_email(email)
        if existing:
            user = existing
            print(f"User exists: {email}")
        else:
            user = await users.create_user(email=email, password=password)
            print(f"Created user: {email} / {password}")

        personas = PersonaService(session)
        plist = await personas.list_for_user(user)
        if plist:
            persona = plist[0]
            print(f"Using persona: {persona.name} ({persona.id})")
        else:
            persona = await personas.create(
                user,
                PersonaCreate(
                    name="Seed Persona",
                    description="Demo digital twin from seed_data.py",
                    system_prompt="You mirror the user's tone and values; stay helpful and honest.",
                ),
            )
            print(f"Created persona: {persona.name} ({persona.id})")

        emb = EmbeddingService()
        memories = MemoryService(session, emb)
        await memories.ingest(
            persona,
            MemoryIngest(
                source_type=MemorySourceType.profile,
                content="The user prefers concise answers, morning workouts, and jazz piano.",
                extra={"seed": True},
            ),
        )
        await memories.ingest(
            persona,
            MemoryIngest(
                source_type=MemorySourceType.document,
                content=(
                    "Project North Star: ship MVP in Q2, focus on first 100 users, "
                    "measure retention."
                ),
                source_ref="seed:doc:1",
                extra={"seed": True},
            ),
        )
        print("Ingested profile + document memories.")


if __name__ == "__main__":
    asyncio.run(main())
