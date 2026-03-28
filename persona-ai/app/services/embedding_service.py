"""Embedding provider: OpenAI-compatible HTTP API or deterministic fake vectors."""

from __future__ import annotations

import hashlib
import math
import struct
from collections.abc import Sequence

import httpx

from app.core.config import get_settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class EmbeddingService:
    def __init__(self) -> None:
        self._settings = get_settings()

    def _fake_vector(self, text: str) -> list[float]:
        """Deterministic pseudo-embedding for local/dev without external API calls."""
        dim = self._settings.embedding_dimensions
        vec: list[float] = []
        seed = hashlib.sha256(text.encode("utf-8")).digest()
        for i in range(dim):
            block = bytes((seed[j % len(seed)] ^ ((i + j) % 251)) for j in range(32))
            val = struct.unpack_from("!f", block[:4])[0]
            vec.append(val)
        norm = math.sqrt(sum(v * v for v in vec)) or 1.0
        return [v / norm for v in vec]

    async def embed_texts(self, texts: Sequence[str]) -> list[list[float]]:
        if not texts:
            return []

        key = (self._settings.embedding_api_key or "").strip()
        if self._settings.embedding_fake:
            return [self._fake_vector(t) for t in texts]

        if not key:
            logger.warning(
                "No EMBEDDING_API_KEY set; using deterministic fake embeddings. "
                "Set EMBEDDING_FAKE=true to acknowledge this for local development."
            )
            return [self._fake_vector(t) for t in texts]

        url = f"{self._settings.embedding_api_base.rstrip('/')}/embeddings"
        headers = {
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": self._settings.embedding_model,
            "input": list(texts),
        }
        async with httpx.AsyncClient(timeout=60.0) as client:
            resp = await client.post(url, json=payload, headers=headers)
            try:
                resp.raise_for_status()
            except httpx.HTTPStatusError as e:
                logger.exception("Embedding API error: %s", e.response.text)
                raise RuntimeError("Embedding provider request failed") from e
            data = resp.json()
        items = data.get("data") or []
        items_sorted = sorted(items, key=lambda x: x.get("index", 0))
        vectors: list[list[float]] = []
        for item in items_sorted:
            emb = item.get("embedding")
            if not isinstance(emb, list):
                raise RuntimeError("Invalid embedding response shape")
            vectors.append([float(x) for x in emb])
        if len(vectors) != len(texts):
            raise RuntimeError("Embedding count mismatch")
        for v in vectors:
            if len(v) != self._settings.embedding_dimensions:
                raise RuntimeError(
                    f"Embedding dimension mismatch: got {len(v)}, "
                    f"expected {self._settings.embedding_dimensions}"
                )
        return vectors

    async def embed_text(self, text: str) -> list[float]:
        return (await self.embed_texts([text]))[0]
