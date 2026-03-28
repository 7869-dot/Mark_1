"""Helpers for pgvector / SQLAlchemy similarity expressions."""

from __future__ import annotations

from typing import Any

from sqlalchemy import Select
from sqlalchemy.sql.elements import ColumnElement

from app.models.memory import Memory


def with_cosine_order(stmt: Select[Any], query_embedding: list[float]) -> Select[Any]:
    """Apply cosine-distance ordering (ascending = most similar first)."""
    distance: ColumnElement[Any] = Memory.embedding.cosine_distance(query_embedding)
    return stmt.order_by(distance.asc())


def cosine_similarity_from_distance(distance: float) -> float:
    """
    pgvector cosine distance `<=>` equals `1 - cosine_similarity` for normalized vectors.
    Map to a 0–1 similarity score for API consumers.
    """
    return max(0.0, min(1.0, 1.0 - float(distance)))
