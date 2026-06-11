"""Rate limiting baseado em `slowapi`.

Limita o número de chamadas por IP/cliente em janelas de 1 minuto e 1 hora.
A função `rate_limit_for_chat` é referenciada no decorador do endpoint e lê os
valores diretamente das `Settings`, permitindo ajuste sem recompilar.
"""

from __future__ import annotations

from slowapi import Limiter
from slowapi.util import get_remote_address

from backend.config import get_settings


def _identify(request) -> str:  # type: ignore[no-untyped-def]
    """Identificador estável para rate-limit.

    Prefere o cabeçalho `X-Forwarded-For` (atrás de proxy) e cai no IP direto.
    """
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return get_remote_address(request)


limiter = Limiter(
    key_func=_identify,
    headers_enabled=True,
    storage_uri="memory://",
)


def rate_limit_for_chat() -> str:
    """Compõe a string de limite a partir das configurações.

    Exemplo: `"20/minute;200/hour"`.
    """
    settings = get_settings()
    return f"{settings.rate_limit_per_minute}/minute;{settings.rate_limit_per_hour}/hour"
