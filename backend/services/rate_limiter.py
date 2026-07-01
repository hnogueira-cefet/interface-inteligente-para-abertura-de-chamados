"""Rate limiting in-memory baseado em janelas deslizantes.

Implementação própria (sem `slowapi`) porque o decorator `@limiter.limit` do
slowapi quebra a inspeção de assinatura do FastAPI moderno, fazendo o
framework tratar dependências como query params. Esta versão é injetada via
`Depends(enforce_rate_limit)`, preservando perfeitamente a tipagem.

Mantém limites por minuto e por hora, identificando cada cliente por
`X-Forwarded-For` (atrás de proxy) ou IP direto.

Para deploy multi-instância, troque o `_LocalRateLimiter` por uma
implementação Redis (incr + expire) — a interface se mantém.
"""

from __future__ import annotations

import threading
import time
from collections import defaultdict, deque
from typing import Deque, Dict

from fastapi import HTTPException, Request, status

from backend.config import Settings, get_settings


class _LocalRateLimiter:
    """Sliding window thread-safe em memória."""

    def __init__(self) -> None:
        self._buckets: Dict[str, Deque[float]] = defaultdict(deque)
        self._lock = threading.Lock()

    def check(self, key: str, per_minute: int, per_hour: int) -> None:
        """Levanta HTTP 429 se o cliente excedeu o limite."""
        now = time.time()
        cutoff_hour = now - 3600
        cutoff_minute = now - 60

        with self._lock:
            bucket = self._buckets[key]

            # Limpa entradas mais antigas que 1h.
            while bucket and bucket[0] < cutoff_hour:
                bucket.popleft()

            count_hour = len(bucket)
            count_minute = sum(1 for t in bucket if t >= cutoff_minute)

            if count_minute >= per_minute or count_hour >= per_hour:
                # Quanto tempo até liberar uma vaga no minuto?
                oldest_in_minute = next((t for t in bucket if t >= cutoff_minute), now)
                retry_after = max(1, int(60 - (now - oldest_in_minute)))
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail=(
                        "Muitas requisições. Aguarde alguns instantes e "
                        "tente novamente."
                    ),
                    headers={"Retry-After": str(retry_after)},
                )

            bucket.append(now)


_limiter_singleton = _LocalRateLimiter()


def _identify(request: Request) -> str:
    """Identifica o cliente para rate-limit."""
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    client = request.client
    if client and client.host:
        return client.host
    return "unknown"


def enforce_rate_limit(request: Request) -> None:
    """Dependência FastAPI: aplica o rate-limit configurado.

    Uso:
        @router.post("/chat", dependencies=[Depends(enforce_rate_limit)])
        async def chat(...): ...
    """
    settings = get_settings()
    key = _identify(request)
    _limiter_singleton.check(
        key=key,
        per_minute=settings.rate_limit_per_minute,
        per_hour=settings.rate_limit_per_hour,
    )
