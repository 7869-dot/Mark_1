"""Persona CRUD scoped to owning user."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.persona import Persona
from app.models.session import PersonaSession
from app.models.user import User
from app.schemas.persona import PersonaCreate, PersonaUpdate


class PersonaService:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def create(self, owner: User, data: PersonaCreate) -> Persona:
        persona = Persona(
            user_id=owner.id,
            name=data.name,
            description=data.description,
            system_prompt=data.system_prompt,
        )
        self._db.add(persona)
        await self._db.commit()
        await self._db.refresh(persona)
        return persona

    async def list_for_user(self, owner: User) -> list[Persona]:
        result = await self._db.execute(
            select(Persona).where(Persona.user_id == owner.id).order_by(Persona.created_at.desc())
        )
        return list(result.scalars().all())

    async def get_owned(self, owner: User, persona_id: UUID) -> Persona | None:
        result = await self._db.execute(
            select(Persona).where(Persona.id == persona_id, Persona.user_id == owner.id)
        )
        return result.scalar_one_or_none()

    async def update(self, persona: Persona, data: PersonaUpdate) -> Persona:
        if data.name is not None:
            persona.name = data.name
        if data.description is not None:
            persona.description = data.description
        if data.system_prompt is not None:
            persona.system_prompt = data.system_prompt
        if data.is_active is not None:
            persona.is_active = data.is_active
        await self._db.commit()
        await self._db.refresh(persona)
        return persona

    async def delete(self, persona: Persona) -> None:
        await self._db.delete(persona)
        await self._db.commit()

    async def create_session(self, persona: Persona, title: str | None) -> PersonaSession:
        session = PersonaSession(persona_id=persona.id, title=title)
        self._db.add(session)
        await self._db.commit()
        await self._db.refresh(session)
        return session
