"""Schemas Pydantic dos endpoints REST.

Espelham (e validam) o contrato declarado na especificação:

    POST /chat
    Request:  { "session_id": "123", "message": "Preciso solicitar histórico" }
    Response: { "response": "Claro! Você é aluno..." }
"""

from __future__ import annotations

from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field, field_validator

from backend.config import get_settings


class MessageRole(str, Enum):
    """Papéis possíveis em uma mensagem do histórico."""

    USER = "user"
    ASSISTANT = "assistant"


class ChatHistoryMessage(BaseModel):
    """Mensagem de histórico enviada opcionalmente pelo cliente.

    Quando o cliente não controla a sessão, o backend usa o `session_id` para
    recuperar o histórico armazenado. Quando o cliente envia `history`, o
    backend mescla com o seu próprio registro (priorizando o do servidor).
    """

    role: MessageRole
    content: str = Field(..., min_length=1)

    @field_validator("content")
    @classmethod
    def _trim_content(cls, value: str) -> str:
        return value.strip()


class ChatRequest(BaseModel):
    """Corpo da requisição de `POST /chat`."""

    session_id: str = Field(
        ...,
        min_length=8,
        max_length=128,
        description="Identificador opaco da sessão (UUID gerado no frontend).",
        examples=["a8b3f0c1-7d2e-4b9c-8e5f-1a2b3c4d5e6f"],
    )
    message: str = Field(
        ...,
        min_length=1,
        description="Mensagem do usuário (texto puro).",
        examples=["Preciso solicitar histórico"],
    )
    history: Optional[List[ChatHistoryMessage]] = Field(
        default=None,
        description=(
            "Histórico opcional enviado pelo cliente. Quando omitido, o backend "
            "usa apenas o histórico interno indexado por `session_id`."
        ),
    )

    @field_validator("session_id")
    @classmethod
    def _validate_session_id(cls, value: str) -> str:
        cleaned = value.strip()
        # Apenas caracteres seguros (UUID, alfanuméricos, hífens, sublinhados).
        allowed = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_")
        if not cleaned or any(c not in allowed for c in cleaned):
            raise ValueError("session_id contém caracteres inválidos")
        return cleaned

    @field_validator("message")
    @classmethod
    def _validate_message(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("message não pode ser vazia")
        max_len = get_settings().max_message_length
        if len(cleaned) > max_len:
            raise ValueError(f"message excede {max_len} caracteres")
        return cleaned


class ChatResponse(BaseModel):
    """Resposta de `POST /chat` — campo principal `response` conforme spec.

    Campos adicionais (`reply`, `session_id`, `model`) são incluídos para
    compatibilidade retroativa com o frontend existente (`reply`) e para
    auditoria — o cliente pode ignorá-los.
    """

    response: str = Field(..., description="Texto da resposta do assistente.")
    reply: str = Field(..., description="Alias de `response` para o frontend atual.")
    session_id: str = Field(..., description="Eco do `session_id` recebido.")
    model: str = Field(..., description="Modelo Llama utilizado.")


class HealthResponse(BaseModel):
    """Resposta do health-check."""

    status: str = "ok"
    service: str
    version: str
    model: str


class ErrorResponse(BaseModel):
    """Formato uniforme de erros."""

    detail: str
    code: Optional[str] = None
