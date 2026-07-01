"""Endpoint POST /chat.

Recebe `{ session_id, message, history? }`, sanitiza, mescla histórico,
consulta a Groq (Llama), persiste a conversa e devolve a resposta.

Inclui:
- Validação de origem via autenticação opcional (X-API-Token).
- *Rate limiting* (slowapi) — limites por minuto e por hora.
- Sanitização de entrada e proteção contra prompt injection.
- Logs estruturados de auditoria (sem expor o conteúdo das mensagens em
  produção; veja `app_env`).
"""

from __future__ import annotations

import asyncio
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Request, status
from groq import GroqError

from backend.api.security import authenticate_request, client_identifier
from backend.config import Settings, get_settings
from backend.models import ChatRequest, ChatResponse, MessageRole
from backend.services.audit_logger import get_logger
from backend.services.groq_client import GroqClient, get_groq_client
from backend.services.rate_limiter import limiter, rate_limit_for_chat
from backend.services.sanitizer import InputSanitizer
from backend.services.session_store import SessionStore, StoredMessage, get_session_store

router = APIRouter(tags=["chat"])
logger = get_logger("cefet.suporte.chat")


def _merge_history(
    server_history: List[StoredMessage],
    client_history: List[StoredMessage] | None,
    max_messages: int,
) -> List[StoredMessage]:
    """Garante que o histórico enviado ao modelo respeite o limite definido.

    Prioridade: histórico do servidor (verdade da sessão). O `client_history`
    serve apenas como *fallback* para o primeiro turno (quando o servidor
    ainda não conhece a sessão).
    """
    base = server_history if server_history else (client_history or [])
    if max_messages <= 0:
        return []
    return base[-max_messages:]


@router.post(
    "/chat",
    response_model=ChatResponse,
    summary="Envia uma mensagem ao Suporte Inteligente",
    dependencies=[Depends(authenticate_request)],
)
@limiter.limit(rate_limit_for_chat)
async def chat(
    request: Request,
    payload: ChatRequest,
    settings: Settings = Depends(get_settings),
    store: SessionStore = Depends(get_session_store),
    groq: GroqClient = Depends(get_groq_client),
) -> ChatResponse:
    client_id = client_identifier(request)

    log = logger.bind(
        session_id=payload.session_id,
        client_id=client_id,
        path=str(request.url.path),
        message_length=len(payload.message),
    )

    sanitizer = InputSanitizer(max_length=settings.max_message_length)
    try:
        sanitized = sanitizer.sanitize(payload.message)
    except ValueError as exc:
        log.warning("rejeitado.sanitize", reason=str(exc))
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    if sanitized.suspicious:
        log.warning(
            "prompt_injection.suspeita",
            patterns=sanitized.flagged_patterns,
        )

    server_history = store.get_history(payload.session_id)
    client_history: List[StoredMessage] | None = None
    if payload.history:
        client_history = [
            StoredMessage(role=h.role.value, content=h.content)
            for h in payload.history
        ]

    history_for_model = _merge_history(
        server_history=server_history,
        client_history=client_history,
        max_messages=settings.max_history_messages,
    )

    wrapped_user_message = InputSanitizer.wrap_user_message(sanitized.text)

    try:
        reply = await asyncio.to_thread(
            groq.generate_reply,
            history_for_model,
            wrapped_user_message,
        )
    except GroqError as exc:
        log.error("groq.error", error=str(exc))
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Não foi possível consultar o modelo neste momento.",
        ) from exc
    except Exception as exc:  # noqa: BLE001 — converter qualquer erro em 500 amigável
        log.exception("chat.error", error=str(exc))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno ao processar a mensagem.",
        ) from exc

    # Persiste sem o envelope — o histórico é uma representação fiel da conversa.
    store.append(payload.session_id, MessageRole.USER.value, sanitized.text)
    store.append(payload.session_id, MessageRole.ASSISTANT.value, reply)

    log.info(
        "chat.ok",
        reply_length=len(reply),
        history_size=len(history_for_model),
        suspicious=sanitized.suspicious,
    )

    return ChatResponse(
        response=reply,
        reply=reply,
        session_id=payload.session_id,
        model=groq.model,
    )
