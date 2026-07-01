"""Testes do endpoint POST /api/pergunta."""

from __future__ import annotations

from fastapi.testclient import TestClient

from backend.main import create_app


def test_pergunta_modo_teste_retorna_lorem_ipsum(monkeypatch) -> None:
    monkeypatch.setenv("API_TOKEN", "")
    monkeypatch.setenv("PERGUNTA_API_MODO", "teste")

    client = TestClient(create_app())
    response = client.post(
        "/api/pergunta",
        json={"pergunta": "Como abro um chamado?"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["pergunta"] == "Como abro um chamado?"
    assert body["modo"] == "teste"
    assert "Lorem ipsum" in body["resposta"]


def test_pergunta_rejeita_corpo_vazio(monkeypatch) -> None:
    monkeypatch.setenv("API_TOKEN", "")

    client = TestClient(create_app())
    response = client.post("/api/pergunta", json={"pergunta": "   "})

    assert response.status_code == 422
