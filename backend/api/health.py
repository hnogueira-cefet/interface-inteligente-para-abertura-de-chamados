"""Endpoints de saúde e metadados do serviço."""

from __future__ import annotations

from fastapi import APIRouter, Depends

from backend import __version__
from backend.config import Settings, get_settings
from backend.models import HealthResponse

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse, summary="Health check")
def health(settings: Settings = Depends(get_settings)) -> HealthResponse:
    return HealthResponse(
        status="ok",
        service=settings.app_name,
        version=__version__,
        model=settings.groq_model,
    )
