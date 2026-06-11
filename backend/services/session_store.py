"""Persistência de contexto das conversas.

Provê uma interface abstrata (`SessionStore`) e uma implementação em memória
adequada para um único processo. Mantém a porta aberta para uma futura
implementação Redis sem mudar o restante do código (princípio de inversão de
dependência — SOLID).
"""

from __future__ import annotations

import threading
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, List

from backend.config import get_settings


@dataclass
class StoredMessage:
    """Mensagem armazenada no histórico."""

    role: str
    content: str
    timestamp: float = field(default_factory=time.time)


@dataclass
class Session:
    """Estado de uma conversa."""

    session_id: str
    messages: List[StoredMessage] = field(default_factory=list)
    created_at: float = field(default_factory=time.time)
    last_activity: float = field(default_factory=time.time)

    def touch(self) -> None:
        self.last_activity = time.time()


class SessionStore(ABC):
    """Contrato para armazenamento de sessões."""

    @abstractmethod
    def get_or_create(self, session_id: str) -> Session: ...

    @abstractmethod
    def append(self, session_id: str, role: str, content: str) -> Session: ...

    @abstractmethod
    def get_history(self, session_id: str) -> List[StoredMessage]: ...

    @abstractmethod
    def clear(self, session_id: str) -> None: ...


class InMemorySessionStore(SessionStore):
    """Store em memória, *thread-safe*, com TTL e limite de mensagens.

    Em produção com múltiplos workers, substitua por uma implementação Redis
    ou banco — o contrato `SessionStore` é o ponto de extensão.
    """

    def __init__(
        self,
        ttl_seconds: int | None = None,
        max_messages: int | None = None,
    ) -> None:
        settings = get_settings()
        self._ttl = ttl_seconds if ttl_seconds is not None else settings.session_ttl_seconds
        self._max_messages = (
            max_messages if max_messages is not None else settings.session_max_messages
        )
        self._sessions: Dict[str, Session] = {}
        self._lock = threading.Lock()

    def _prune_expired_locked(self) -> None:
        if self._ttl <= 0:
            return
        cutoff = time.time() - self._ttl
        expired = [sid for sid, s in self._sessions.items() if s.last_activity < cutoff]
        for sid in expired:
            del self._sessions[sid]

    def get_or_create(self, session_id: str) -> Session:
        with self._lock:
            self._prune_expired_locked()
            session = self._sessions.get(session_id)
            if session is None:
                session = Session(session_id=session_id)
                self._sessions[session_id] = session
            else:
                session.touch()
            return session

    def append(self, session_id: str, role: str, content: str) -> Session:
        with self._lock:
            self._prune_expired_locked()
            session = self._sessions.get(session_id)
            if session is None:
                session = Session(session_id=session_id)
                self._sessions[session_id] = session
            session.messages.append(StoredMessage(role=role, content=content))
            if len(session.messages) > self._max_messages:
                drop = len(session.messages) - self._max_messages
                session.messages = session.messages[drop:]
            session.touch()
            return session

    def get_history(self, session_id: str) -> List[StoredMessage]:
        with self._lock:
            session = self._sessions.get(session_id)
            if session is None:
                return []
            return list(session.messages)

    def clear(self, session_id: str) -> None:
        with self._lock:
            self._sessions.pop(session_id, None)


_store_singleton: SessionStore | None = None
_store_lock = threading.Lock()


def get_session_store() -> SessionStore:
    """Singleton do store em memória (injetado via FastAPI Depends)."""
    global _store_singleton
    if _store_singleton is None:
        with _store_lock:
            if _store_singleton is None:
                _store_singleton = InMemorySessionStore()
    return _store_singleton
