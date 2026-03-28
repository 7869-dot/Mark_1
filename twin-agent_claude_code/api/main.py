"""
api/main.py

FastAPI application entry point.

Starts the server, mounts all routers, exposes health check.
Your co-founder hits these endpoints from the frontend.

Run with:
    uvicorn api.main:app --reload --host 0.0.0.0 --port 8000

Interactive docs at: http://localhost:8000/docs
"""

from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routes.agent import get_agent, router as agent_router
from api.routes.memory import get_semantic, router as memory_router
from api.schemas import HealthResponse
from config.logging import get_logger, setup_logging
from config.settings import settings

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown logic."""
    setup_logging()
    logger.info("server_starting", model=settings.llm_model, debug=settings.debug)

    # Pre-warm the agent and memory on startup so first request isn't slow
    try:
        agent = get_agent()
        semantic = get_semantic()
        logger.info(
            "server_ready",
            tools=len(agent.registry),
            memory_entries=semantic.count(),
        )
    except Exception as e:
        logger.error("startup_failed", error=str(e))
        raise

    yield

    logger.info("server_shutting_down")


app = FastAPI(
    title="Twin Agent API",
    description=(
        "Autonomous AI agent backend. "
        "The agent can read/send email, post to Slack and Twitter, "
        "browse the web, and remember context across sessions."
    ),
    version="0.1.0",
    lifespan=lifespan,
)

# CORS — allows your co-founder's frontend (any origin in dev, restrict in prod)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if settings.debug else ["https://yourdomain.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount routers
app.include_router(agent_router)
app.include_router(memory_router)


@app.get("/health", response_model=HealthResponse, tags=["system"])
def health():
    """
    Health check endpoint.
    Returns agent status, model info, and memory stats.
    """
    agent = get_agent()
    semantic = get_semantic()

    return HealthResponse(
        status="ok",
        agent_name=settings.agent_name,
        model=settings.llm_model,
        tools_available=len(agent.registry),
        memory_entries=semantic.count(),
    )


@app.get("/", tags=["system"])
def root():
    return {
        "name": "Twin Agent API",
        "version": "0.1.0",
        "docs": "/docs",
        "health": "/health",
    }
