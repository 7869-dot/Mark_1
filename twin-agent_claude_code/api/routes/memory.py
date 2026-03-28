"""
api/routes/memory.py

Memory endpoints:
  POST   /memory/search   — semantic search
  POST   /memory/store    — store a fact or note
  DELETE /memory/{id}     — delete a memory entry
  GET    /memory/count    — how many entries in the vector store
"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from api.schemas import (
    MemorySearchRequest,
    MemorySearchResponse,
    MemorySearchResult,
    MemoryStoreRequest,
    MemoryStoreResponse,
)
from config.logging import get_logger
from memory.semantic import SemanticMemory

logger = get_logger(__name__)
router = APIRouter(prefix="/memory", tags=["memory"])

_semantic: SemanticMemory | None = None


def get_semantic() -> SemanticMemory:
    global _semantic
    if _semantic is None:
        _semantic = SemanticMemory()
    return _semantic


@router.post("/search", response_model=MemorySearchResponse)
def search_memory(request: MemorySearchRequest):
    """Search semantic memory for relevant facts and past context."""
    semantic = get_semantic()
    raw = semantic.search(request.query, n_results=request.n_results)

    results = [
        MemorySearchResult(
            id=r["id"],
            text=r["text"],
            metadata=r["metadata"],
            distance=r["distance"],
            similarity=round(1 - r["distance"], 3),
        )
        for r in raw
    ]

    return MemorySearchResponse(
        query=request.query,
        results=results,
        total=len(results),
    )


@router.post("/store", response_model=MemoryStoreResponse)
def store_memory(request: MemoryStoreRequest):
    """Manually store a fact or note in semantic memory."""
    semantic = get_semantic()
    doc_id = semantic.store(text=request.text, metadata=request.metadata)
    return MemoryStoreResponse(id=doc_id, message=f"Stored with ID: {doc_id}")


@router.delete("/{doc_id}")
def delete_memory(doc_id: str):
    """Delete a specific memory entry by ID."""
    semantic = get_semantic()
    try:
        semantic.delete(doc_id)
        return {"message": f"Deleted memory: {doc_id}"}
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/count")
def memory_count():
    """Return the total number of entries in semantic memory."""
    semantic = get_semantic()
    return {"count": semantic.count()}
