"""Persona schemas and memory chunking unit tests."""

from __future__ import annotations

from app.schemas.persona import PersonaCreate
from app.utils.chunking import chunk_text


def test_persona_create_schema() -> None:
    p = PersonaCreate(name="Ada", description="Explorer", system_prompt="Be concise.")
    assert p.name == "Ada"
    assert p.description == "Explorer"


def test_chunking_produces_multiple_chunks_with_overlap() -> None:
    text = ("word " * 400).strip()
    chunks = chunk_text(text, chunk_size=120, overlap=30)
    assert len(chunks) >= 2
    assert all(len(c) <= 120 for c in chunks)


def test_chunking_empty_returns_empty() -> None:
    assert chunk_text("   \n\t  ") == []
