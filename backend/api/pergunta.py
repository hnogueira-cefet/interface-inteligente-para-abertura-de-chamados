"""Endpoint POST /api/pergunta — integração externa simplificada.

Contrato pensado para sistemas terceiros que enviam a pergunta do usuário e
recebem uma resposta, sem precisar gerenciar `session_id` ou histórico.

No modo `teste` (padrão), devolve Lorem Ipsum para validar a comunicação.
No modo `ia`, consulta o mesmo modelo Llama usado pelo chat principal.
"""

from __future__ import annotations

import asyncio
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, status
from groq import GroqError

from backend.api.security import authenticate_request, client_identifier
from backend.config import Settings, get_settings
from backend.models import PerguntaRequest, PerguntaResponse
from backend.services.audit_logger import get_logger
from backend.services.groq_client import GroqClient, get_groq_client
from backend.services.rate_limiter import enforce_rate_limit
from backend.services.sanitizer import InputSanitizer

router = APIRouter(prefix="/api", tags=["integração"])
logger = get_logger("cefet.suporte.pergunta")

LOREM_IPSUM_RESPOSTA = (
    "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod "
    "tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim "
    "veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea "
    "commodo consequat."
)


@router.post(
    "/pergunta",
    response_model=PerguntaResponse,
    summary="Envia uma pergunta e recebe uma resposta",
    description=(
        "API simplificada para integrações externas. Recebe apenas o texto da "
        "pergunta e devolve uma resposta. No modo padrão (`PERGUNTA_API_MODO=teste`), "
        "retorna Lorem Ipsum para validação da comunicação."
    ),
    dependencies=[
        Depends(authenticate_request),
        Depends(enforce_rate_limit),
    ],
)
async def responder_pergunta(
    request: Request,
    payload: PerguntaRequest,
    settings: Annotated[Settings, Depends(get_settings)],
    groq: Annotated[GroqClient, Depends(get_groq_client)],
) -> PerguntaResponse:
    client_id = client_identifier(request)
    modo = settings.pergunta_api_modo.strip().lower()

    log = logger.bind(
        client_id=client_id,
        path=str(request.url.path),
        pergunta_length=len(payload.pergunta),
        modo=modo,
    )

    sanitizer = InputSanitizer(max_length=settings.max_message_length)
    try:
        sanitized = sanitizer.sanitize(payload.pergunta)
    except ValueError as exc:
        log.warning("rejeitado.sanitize", reason=str(exc))
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    if modo == "teste":
        log.info("pergunta.ok", stub=True)
        return PerguntaResponse(
            pergunta=sanitized.text,
            resposta=LOREM_IPSUM_RESPOSTA,
            modo="teste",
        )

    if modo != "ia":
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Configuração inválida: PERGUNTA_API_MODO deve ser 'teste' ou 'ia'.",
        )

    wrapped = InputSanitizer.wrap_user_message(sanitized.text)
    try:
        resposta = await asyncio.to_thread(
            groq.generate_reply,
            [],
            wrapped,
        )
    except GroqError as exc:
        log.error("groq.error", error=str(exc))
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Não foi possível consultar o modelo neste momento.",
        ) from exc
    except Exception as exc:  # noqa: BLE001
        log.exception("pergunta.error", error=str(exc))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno ao processar a pergunta.",
        ) from exc

    log.info("pergunta.ok", stub=False, resposta_length=len(resposta))
    return PerguntaResponse(
        pergunta=sanitized.text,
        resposta=resposta,
        modo="ia",
    )
