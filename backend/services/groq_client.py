"""Cliente para o modelo Llama hospedado na Groq."""

from __future__ import annotations

import threading
from typing import Iterable, List

from groq import Groq

from backend.config import Settings, get_settings
from backend.models import MessageRole
from backend.prompts import build_system_prompt
from backend.services.session_store import StoredMessage


class GroqConfigurationError(RuntimeError):
    """Levantado quando a configuração da Groq é inválida."""


class GroqClient:
    """Wrapper fino sobre o SDK oficial da Groq.

    Recebe o histórico já tratado e devolve a resposta do modelo. Não fala com
    o store de sessões — manter responsabilidades isoladas (S do SOLID).
    """

    def __init__(self, settings: Settings | None = None) -> None:
        self._settings = settings or get_settings()
        if not self._settings.groq_api_key:
            raise GroqConfigurationError(
                "GROQ_API_KEY não está configurada. Defina a variável no .env."
            )
        self._client = Groq(
            api_key=self._settings.groq_api_key,
            timeout=self._settings.groq_timeout_seconds,
        )

    @property
    def model(self) -> str:
        return self._settings.groq_model

    def _build_messages(
        self,
        history: Iterable[StoredMessage],
        user_message: str,
        extra_system_context: str | None = None,
    ) -> List[dict[str, str]]:
        """Monta a lista de mensagens no formato esperado pela API."""
        messages: List[dict[str, str]] = [
            {"role": "system", "content": build_system_prompt(extra_system_context)},
        ]

        for entry in history:
            role = (
                MessageRole.USER.value
                if entry.role == MessageRole.USER.value
                else MessageRole.ASSISTANT.value
            )
            content = (entry.content or "").strip()
            if not content:
                continue
            messages.append({"role": role, "content": content})

        messages.append({"role": MessageRole.USER.value, "content": user_message})
        return messages

    def generate_reply(
        self,
        history: Iterable[StoredMessage],
        user_message: str,
        extra_system_context: str | None = None,
    ) -> str:
        """Solicita uma resposta ao modelo e devolve o texto plano."""
        messages = self._build_messages(history, user_message, extra_system_context)

        completion = self._client.chat.completions.create(
            model=self._settings.groq_model,
            messages=messages,
            temperature=self._settings.groq_temperature,
            max_tokens=self._settings.groq_max_tokens,
            top_p=0.9,
            stream=False,
        )

        if not completion.choices:
            raise RuntimeError("A Groq retornou uma resposta vazia.")

        reply = completion.choices[0].message.content or ""
        reply = reply.strip()
        if not reply:
            raise RuntimeError("Resposta do modelo veio em branco.")
        return reply


_client_singleton: GroqClient | None = None
_client_lock = threading.Lock()


def get_groq_client() -> GroqClient:
    """Singleton do cliente Groq (injetado via FastAPI Depends)."""
    global _client_singleton
    if _client_singleton is None:
        with _client_lock:
            if _client_singleton is None:
                _client_singleton = GroqClient()
    return _client_singleton
