"""
config/logging.py

Structured logging using structlog.
Every log line is a JSON object in production, readable rich text in dev.
"""

import logging
import sys
import structlog
from config.settings import settings


def setup_logging() -> None:
    """Configure structlog for the entire application. Call once at startup."""

    log_level = logging.DEBUG if settings.debug else logging.INFO

    # Standard library logging baseline
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=log_level,
    )

    # Processors applied to every log event
    shared_processors = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
    ]

    if settings.debug:
        # Human-readable coloured output for local development
        processors = shared_processors + [
            structlog.dev.ConsoleRenderer(),
        ]
    else:
        # Machine-readable JSON for production / log aggregators
        processors = shared_processors + [
            structlog.processors.dict_tracebacks,
            structlog.processors.JSONRenderer(),
        ]

    structlog.configure(
        processors=processors,
        wrapper_class=structlog.make_filtering_bound_logger(log_level),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )


def get_logger(name: str):
    """Return a bound structlog logger for the given module name."""
    return structlog.get_logger(name)
