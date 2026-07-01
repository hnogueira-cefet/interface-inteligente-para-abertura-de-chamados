"""Routers da API REST."""

from backend.api.chat import router as chat_router
from backend.api.health import router as health_router

__all__ = ["chat_router", "health_router"]
