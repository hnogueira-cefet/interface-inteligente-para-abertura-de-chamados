"""Dependências de segurança (autenticação opcional, identidade da chamada)."""

from __future__ import annotations

from fastapi import Depends, HTTPException, Request, status

from backend.config import Settings, get_settings


def authenticate_request(
    request: Request,
    settings: Settings = Depends(get_settings),
) -> None:
    """Valida o header `X-API-Token` (quando configurado).

    Quando `API_TOKEN` não está definido no `.env`, a autenticação fica
    desabilitada — útil para o ambiente local. Em produção configure SEMPRE o
    token; o frontend (server function do TanStack) envia o valor a partir de
    uma variável server-only.
    """
    expected = settings.api_token
    if not expected:
        return

    provided = request.headers.get("x-api-token")
    if not provided or provided != expected:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token de API inválido ou ausente.",
        )


def client_identifier(request: Request) -> str:
    """Identifica o cliente para *rate limiting* e auditoria.

    Prioriza `X-Forwarded-For` (atrás de proxy), recai no IP direto e, em
    último caso, no `session_id` enviado no corpo da requisição.
    """
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    client = request.client
    if client and client.host:
        return client.host
    return "unknown"
