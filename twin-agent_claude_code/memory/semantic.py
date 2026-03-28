"""
memory/semantic.py

Semantic memory — stores facts, knowledge, and summaries as vector embeddings.
Similarity search lets the agent retrieve relevant context before a task,
so it remembers things across sessions without stuffing everything in the prompt.

Storage: ChromaDB (runs in-process, no server needed for dev).
Migration path: swap to pgvector on Supabase for production scale.
"""

from __future__ import annotations

import hashlib
import json
import os
from datetime import datetime, timezone
from typing import Any

import chromadb
from chromadb.utils import embedding_functions

from config.logging import get_logger
from config.settings import settings

logger = get_logger(__name__)

COLLECTION_NAME = "twin_agent_memory"


class SemanticMemory:
    """
    Vector-based long-term memory.

    Usage:
        mem = SemanticMemory()
        mem.store("User prefers short emails. Always be concise.", {"type": "preference"})
        results = mem.search("email style preferences", n_results=3)
    """

    def __init__(self) -> None:
        os.makedirs(settings.chroma_persist_path, exist_ok=True)

        self._client = chromadb.PersistentClient(path=settings.chroma_persist_path)

        # Use a local sentence-transformer for embeddings (no API calls, no cost)
        self._embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name=settings.embedding_model
        )

        self._collection = self._client.get_or_create_collection(
            name=COLLECTION_NAME,
            embedding_function=self._embedding_fn,
            metadata={"hnsw:space": "cosine"},
        )

        logger.info(
            "semantic_memory_init",
            path=settings.chroma_persist_path,
            collection=COLLECTION_NAME,
            count=self._collection.count(),
        )

    def store(
        self,
        text: str,
        metadata: dict[str, Any] | None = None,
        doc_id: str | None = None,
    ) -> str:
        """
        Store a text chunk in the vector store.

        Args:
            text:     The text to embed and store
            metadata: Optional key-value tags (type, session_id, source, etc.)
            doc_id:   Optional stable ID — same ID overwrites previous entry

        Returns:
            The document ID
        """
        if not text.strip():
            raise ValueError("Cannot store empty text in semantic memory")

        # Generate a stable ID from content if not provided
        _id = doc_id or hashlib.sha256(text.encode()).hexdigest()[:16]

        meta = {
            "stored_at": datetime.now(timezone.utc).isoformat(),
            **(metadata or {}),
        }
        # ChromaDB metadata values must be str/int/float/bool
        meta = {k: str(v) if not isinstance(v, (str, int, float, bool)) else v for k, v in meta.items()}

        self._collection.upsert(
            ids=[_id],
            documents=[text],
            metadatas=[meta],
        )

        logger.debug("semantic_store", id=_id, text_preview=text[:60])
        return _id

    def store_many(self, entries: list[dict[str, Any]]) -> list[str]:
        """
        Bulk store. Each entry: {"text": str, "metadata": dict, "id": str (optional)}
        """
        ids = []
        for entry in entries:
            _id = self.store(
                text=entry["text"],
                metadata=entry.get("metadata"),
                doc_id=entry.get("id"),
            )
            ids.append(_id)
        return ids

    def search(self, query: str, n_results: int = 5, where: dict | None = None) -> list[dict]:
        """
        Find the most semantically similar stored memories.

        Args:
            query:     Natural language search query
            n_results: How many results to return
            where:     Optional metadata filter e.g. {"type": "preference"}

        Returns:
            List of dicts with keys: id, text, metadata, distance
        """
        if self._collection.count() == 0:
            return []

        kwargs: dict[str, Any] = {
            "query_texts": [query],
            "n_results": min(n_results, self._collection.count()),
            "include": ["documents", "metadatas", "distances"],
        }
        if where:
            kwargs["where"] = where

        results = self._collection.query(**kwargs)

        output = []
        for i, doc_id in enumerate(results["ids"][0]):
            output.append(
                {
                    "id": doc_id,
                    "text": results["documents"][0][i],
                    "metadata": results["metadatas"][0][i],
                    "distance": results["distances"][0][i],
                }
            )

        logger.debug("semantic_search", query=query[:60], n_results=len(output))
        return output

    def format_for_prompt(self, query: str, n_results: int = 4) -> str:
        """
        Search and format results as a readable block for injection into prompts.
        Returns empty string if nothing relevant is found.
        """
        results = self.search(query, n_results=n_results)
        if not results:
            return ""

        lines = []
        for r in results:
            score = 1 - r["distance"]  # cosine similarity
            if score < 0.3:  # Skip low-relevance results
                continue
            lines.append(f"- {r['text']}")

        return "\n".join(lines) if lines else ""

    def delete(self, doc_id: str) -> None:
        self._collection.delete(ids=[doc_id])
        logger.debug("semantic_delete", id=doc_id)

    def count(self) -> int:
        return self._collection.count()
