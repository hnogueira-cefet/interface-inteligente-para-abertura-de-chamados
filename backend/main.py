"""Bootstrap da aplicação FastAPI.

Para executar localmente:
    uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload

Para Docker / produção, ver `backend/Dockerfile` e `docker-compose.yml`.
"""

from __future__ import annotations

from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from backend import __version__
from backend.api import chat_router, health_router, pergunta_router
from backend.config import get_settings
from backend.services import configure_logging, get_logger


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    configure_logging()
    log = get_logger("cefet.suporte.boot")
    settings = get_settings()
    log.info(
        "app.startup",
        app=settings.app_name,
        env=settings.app_env,
        model=settings.groq_model,
        version=__version__,
    )
    yield
    log.info("app.shutdown")


def create_app() -> FastAPI:
    settings = get_settings()

    app = FastAPI(
        title=settings.app_name,
        version=__version__,
        description=(
            "API REST do Suporte Inteligente CEFET/RJ — orienta alunos sobre "
            "abertura de chamados acadêmicos e administrativos."
        ),
        docs_url="/docs" if settings.app_env != "production" else None,
        redoc_url="/redoc" if settings.app_env != "production" else None,
        openapi_url="/openapi.json",
        lifespan=lifespan,
    )

    # CORS — controle de origem (proteção contra spam cross-origin)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "OPTIONS"],
        allow_headers=["*"],
        max_age=86400,
    )

    # Handlers globais
    @app.exception_handler(RequestValidationError)
    async def _validation_handler(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        get_logger("cefet.suporte.validation").info(
            "validation.error",
            path=str(request.url.path),
            errors=exc.errors(),
        )
        return JSONResponse(
            status_code=422,
            content={"detail": "Requisição inválida.", "code": "invalid_request"},
        )

    # Routers
    app.include_router(health_router)
    app.include_router(chat_router)
    app.include_router(pergunta_router)

    return app


app = create_app()


if __name__ == "__main__":  # pragma: no cover
    import uvicorn

    settings = get_settings()
    uvicorn.run(
        "backend.main:app",
        host=settings.app_host,
        port=settings.app_port,
        reload=settings.app_debug,
    )
