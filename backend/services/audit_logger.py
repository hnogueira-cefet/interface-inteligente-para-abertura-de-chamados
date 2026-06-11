"""Configuração de logs estruturados (auditoria)."""

from __future__ import annotations

import logging
import sys
from typing import Any

import structlog

from backend.config import get_settings


def configure_logging() -> None:
    """Configura `structlog` para emitir logs estruturados.

    Em produção (`LOG_FORMAT=json`) os eventos são serializados em JSON, prontos
    para serem ingeridos por sistemas de observabilidade. Em desenvolvimento o
    formato é colorido e amigável ao terminal.
    """
    settings = get_settings()
    level = getattr(logging, settings.log_level.upper(), logging.INFO)

    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=level,
    )

    processors: list[Any] = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso", utc=True),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
    ]

    if settings.log_format == "json":
        processors.append(structlog.processors.JSONRenderer())
    else:
        processors.append(structlog.dev.ConsoleRenderer(colors=True))

    structlog.configure(
        processors=processors,
        wrapper_class=structlog.make_filtering_bound_logger(level),
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )


def get_logger(name: str = "cefet.suporte") -> structlog.stdlib.BoundLogger:
    """Devolve um logger nomeado."""
    return structlog.get_logger(name)
