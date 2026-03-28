"""Personas and lightweight session containers."""

from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status

from app.core.config import get_settings
from app.dependencies import CurrentUser, DbSession, limiter
from app.models.persona import Persona
from app.schemas.persona import (
    PersonaCreate,
    PersonaRead,
    PersonaSessionCreate,
    PersonaSessionRead,
    PersonaUpdate,
)
from app.services.persona_service import PersonaService

_settings = get_settings()

router = APIRouter(prefix="/personas", tags=["personas"])


def get_persona_service(db: DbSession) -> PersonaService:
    return PersonaService(db)


PersonaServiceDep = Annotated[PersonaService, Depends(get_persona_service)]


async def get_owned_persona(
    persona_id: UUID,
    current: CurrentUser,
    personas: PersonaServiceDep,
) -> Persona:
    p = await personas.get_owned(current, persona_id)
    if p is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "persona_not_found", "message": "Persona not found"},
        )
    return p


OwnedPersona = Annotated[Persona, Depends(get_owned_persona)]


@router.post(
    "/",
    response_model=PersonaRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create persona",
)
@limiter.limit(_settings.rate_limit_default)
async def create_persona(
    request: Request,
    body: PersonaCreate,
    current: CurrentUser,
    personas: PersonaServiceDep,
) -> Persona:
    return await personas.create(current, body)


@router.get("/", response_model=list[PersonaRead], summary="List my personas")
@limiter.limit(_settings.rate_limit_default)
async def list_personas(
    request: Request,
    current: CurrentUser,
    personas: PersonaServiceDep,
) -> list[Persona]:
    return await personas.list_for_user(current)


@router.get("/{persona_id}", response_model=PersonaRead, summary="Get persona")
@limiter.limit(_settings.rate_limit_default)
async def get_persona(request: Request, persona: OwnedPersona) -> Persona:
    return persona


@router.patch("/{persona_id}", response_model=PersonaRead, summary="Update persona")
@limiter.limit(_settings.rate_limit_default)
async def update_persona(
    request: Request,
    body: PersonaUpdate,
    persona: OwnedPersona,
    personas: PersonaServiceDep,
) -> Persona:
    return await personas.update(persona, body)


@router.delete("/{persona_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete persona")
@limiter.limit(_settings.rate_limit_default)
async def delete_persona(
    request: Request,
    persona: OwnedPersona,
    personas: PersonaServiceDep,
) -> Response:
    await personas.delete(persona)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post(
    "/{persona_id}/sessions",
    response_model=PersonaSessionRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create chat/session record for this persona",
)
@limiter.limit(_settings.rate_limit_default)
async def create_session(
    request: Request,
    body: PersonaSessionCreate,
    persona: OwnedPersona,
    personas: PersonaServiceDep,
) -> PersonaSessionRead:
    s = await personas.create_session(persona, body.title)
    return PersonaSessionRead.model_validate(s)
