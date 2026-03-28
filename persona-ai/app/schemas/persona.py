"""Persona Pydantic schemas."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class PersonaCreate(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    description: str | None = Field(default=None, max_length=10_000)
    system_prompt: str | None = Field(default=None, max_length=50_000)


class PersonaUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = Field(default=None, max_length=10_000)
    system_prompt: str | None = Field(default=None, max_length=50_000)
    is_active: bool | None = None


class PersonaRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    name: str
    description: str | None
    system_prompt: str | None
    is_active: bool
    created_at: datetime
    updated_at: datetime


class PersonaSessionCreate(BaseModel):
    title: str | None = Field(default=None, max_length=300)


class PersonaSessionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    persona_id: UUID
    title: str | None
    created_at: datetime
