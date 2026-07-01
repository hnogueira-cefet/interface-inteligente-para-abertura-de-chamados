"""Schemas Pydantic da API."""

from backend.models.schemas import (
    ChatHistoryMessage,
    ChatRequest,
    ChatResponse,
    ErrorResponse,
    HealthResponse,
    MessageRole,
    PerguntaRequest,
    PerguntaResponse,
)

__all__ = [
    "ChatHistoryMessage",
    "ChatRequest",
    "ChatResponse",
    "ErrorResponse",
    "HealthResponse",
    "MessageRole",
    "PerguntaRequest",
    "PerguntaResponse",
]
