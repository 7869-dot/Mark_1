"""Text chunking for memory ingestion (lightweight, no extra frameworks)."""

from __future__ import annotations

import re


def chunk_text(
    text: str,
    *,
    chunk_size: int = 1200,
    overlap: int = 200,
) -> list[str]:
    """
    Split text into overlapping chunks by characters (after normalizing whitespace).

    Tuned for short MVP documents and chat transcripts; swap for token-based
    chunking when you move beyond ~100 active users with large corpora.
    """
    cleaned = re.sub(r"\s+", " ", text or "").strip()
    if not cleaned:
        return []

    if chunk_size <= 0:
        raise ValueError("chunk_size must be positive")
    if overlap < 0 or overlap >= chunk_size:
        raise ValueError("overlap must be in [0, chunk_size)")

    chunks: list[str] = []
    start = 0
    n = len(cleaned)
    while start < n:
        end = min(start + chunk_size, n)
        piece = cleaned[start:end].strip()
        if piece:
            chunks.append(piece)
        if end >= n:
            break
        start = end - overlap
        if start < 0:
            start = 0
    return chunks
