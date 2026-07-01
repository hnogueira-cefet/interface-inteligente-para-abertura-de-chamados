"""Configurações centralizadas carregadas a partir do .env.

Usa `pydantic-settings` para validar tipos e fornecer valores default. Cada
nova configuração deve ser declarada aqui (e nunca lida diretamente de
`os.environ` no resto da aplicação) — isso mantém SOLID/Clean Code e facilita
testes.
"""

from __future__ import annotations

from functools import lru_cache
from typing import Annotated, List

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict


class Settings(BaseSettings):
    """Variáveis de ambiente da aplicação."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ────────── Aplicação ──────────
    app_name: str = Field(default="Suporte Inteligente CEFET/RJ")
    app_env: str = Field(default="development")
    app_host: str = Field(default="0.0.0.0")
    app_port: int = Field(default=8000)
    app_debug: bool = Field(default=False)

    # ────────── Groq / LLM ──────────
    groq_api_key: str = Field(
        default="",
        description="Chave da API Groq (https://console.groq.com).",
    )
    groq_model: str = Field(
        default="llama-3.3-70b-versatile",
        description="Modelo Llama hospedado na Groq.",
    )
    groq_temperature: float = Field(default=0.3, ge=0.0, le=2.0)
    groq_max_tokens: int = Field(default=1024, ge=64, le=8192)
    groq_timeout_seconds: float = Field(default=30.0, ge=5.0, le=120.0)

    # ────────── Sessões ──────────
    session_ttl_seconds: int = Field(
        default=60 * 60 * 2,  # 2 horas
        description="Tempo de vida da sessão em memória.",
    )
    session_max_messages: int = Field(
        default=40,
        description="Máximo de mensagens preservadas por sessão.",
    )

    # ────────── Segurança ──────────
    api_token: str = Field(
        default="",
        description=(
            "Token compartilhado entre o frontend (server function) e o backend "
            "Python. Quando vazio, a autenticação é desabilitada (somente para "
            "desenvolvimento local)."
        ),
    )
    rate_limit_per_minute: int = Field(default=20, ge=1, le=1000)
    rate_limit_per_hour: int = Field(default=200, ge=1, le=10000)
    max_message_length: int = Field(default=2000, ge=10, le=8000)
    max_history_messages: int = Field(default=20, ge=0, le=100)

    # ────────── CORS ──────────
    # `NoDecode` impede o pydantic-settings de tentar parsear a string do .env
    # como JSON (List[str] aciona o decode automático). Assim o validator
    # `_parse_origins` abaixo recebe a string crua e faz o split por vírgula.
    allowed_origins: Annotated[List[str], NoDecode] = Field(
        default_factory=lambda: [
            "http://localhost:3000",
            "http://localhost:5173",
            "http://localhost:8080",
            "http://127.0.0.1:3000",
            "http://127.0.0.1:5173",
            "http://127.0.0.1:8080",
        ],
        description="Origens permitidas para CORS.",
    )

    # ────────── Logs ──────────
    log_level: str = Field(default="INFO")
    log_format: str = Field(
        default="json",
        description='Formato dos logs: "json" (produção) ou "console" (dev).',
    )

    # ────────── API de integração (/api/pergunta) ──────────
    pergunta_api_modo: str = Field(
        default="teste",
        description=(
            'Modo da API simplificada: "teste" (Lorem Ipsum) ou "ia" (Llama/Groq).'
        ),
    )

    @field_validator("allowed_origins", mode="before")
    @classmethod
    def _parse_origins(cls, value: object) -> object:
        """Aceita lista separada por vírgula no .env."""
        if isinstance(value, str):
            return [origin.strip() for origin in value.split(",") if origin.strip()]
        return value


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Singleton de Settings (cache em processo)."""
    return Settings()
