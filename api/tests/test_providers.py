"""BYOK: criptografia, mascaramento, isolamento e fallback."""

from __future__ import annotations

from typing import Any

import httpx
import pytest
from httpx import AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.providers import client as provider_client
from app.security.keys import decrypt_secret

from .helpers import PASSWORD, login, make_user

SECRET = "gsk_chave_super_secreta_1234567890"
HINT = "gsk…7890"


async def test_criar_e_listar_sem_expor_chave(client: AsyncClient, session: AsyncSession) -> None:
    await make_user(session, "owner@example.com", role="owner")
    await login(client, "owner@example.com")

    created = await client.post("/me/providers", json={"provider": "groq", "api_key": SECRET})
    assert created.status_code == 201, created.text
    data = created.json()
    assert data["provider"] == "groq"
    assert data["key_hint"] == HINT
    assert data["base_url"] == "https://api.groq.com/openai/v1"
    assert data["model"] == "llama-3.3-70b-versatile"
    assert "api_key" not in data
    assert "api_key_encrypted" not in data

    listed = await client.get("/me/providers")
    assert listed.status_code == 200
    body = listed.json()
    assert [item["provider"] for item in body["items"]] == ["groq"]
    assert body["fallback_order"] == ["groq", "ollama_cloud", "openrouter", "ollama"]
    assert body["offline_mode"] is False
    assert {item["slug"] for item in body["catalog"]} == {
        "groq",
        "ollama_cloud",
        "openrouter",
        "ollama",
    }
    assert SECRET not in listed.text


async def test_chave_fica_criptografada_no_banco(
    client: AsyncClient, session: AsyncSession
) -> None:
    await make_user(session, "owner@example.com", role="owner")
    await login(client, "owner@example.com")
    await client.post("/me/providers", json={"provider": "groq", "api_key": SECRET})

    stored = (
        await session.execute(text("SELECT api_key_encrypted FROM provider_credentials"))
    ).scalar_one()
    assert stored != SECRET
    assert SECRET not in stored
    assert decrypt_secret(stored) == SECRET


@pytest.mark.parametrize(
    "payload",
    [
        {"provider": "groq"},
        {"provider": "ollama", "api_key": SECRET},
        {"provider": "ollama", "base_url": "ftp://localhost:11434"},
        {"provider": "groq", "base_url": "http://api.groq.com/v1", "api_key": SECRET},
        {"provider": "desconhecido", "api_key": SECRET},
    ],
)
async def test_payload_invalido_e_rejeitado(
    client: AsyncClient, session: AsyncSession, payload: dict[str, Any]
) -> None:
    await make_user(session, "owner@example.com", role="owner")
    await login(client, "owner@example.com")

    response = await client.post("/me/providers", json=payload)

    assert response.status_code == 422


async def test_atualizar_e_remover(client: AsyncClient, session: AsyncSession) -> None:
    await make_user(session, "owner@example.com", role="owner")
    await login(client, "owner@example.com")
    await client.post("/me/providers", json={"provider": "groq", "api_key": SECRET})

    updated = await client.patch(
        "/me/providers/groq",
        json={"api_key": "gsk_nova_chave_abcdefgh", "model": "modelo-novo", "is_active": False},
    )
    assert updated.status_code == 200, updated.text
    data = updated.json()
    assert data["key_hint"] == "gsk…efgh"
    assert data["model"] == "modelo-novo"
    assert data["is_active"] is False
    assert "api_key" not in data

    missing = await client.patch("/me/providers/openrouter", json={"model": "x"})
    assert missing.status_code == 404

    deleted = await client.delete("/me/providers/groq")
    assert deleted.status_code == 204
    assert (await client.get("/me/providers")).json()["items"] == []


async def test_isolamento_entre_usuarios(client: AsyncClient, session: AsyncSession) -> None:
    await make_user(session, "alice@example.com", role="owner")
    await make_user(session, "bob@example.com")
    await login(client, "alice@example.com")
    await client.post("/me/providers", json={"provider": "groq", "api_key": SECRET})

    await client.post("/auth/logout")
    await login(client, "bob@example.com")

    assert (await client.get("/me/providers")).json()["items"] == []
    assert (await client.patch("/me/providers/groq", json={"model": "roubado"})).status_code == 404
    assert (await client.delete("/me/providers/groq")).status_code == 404
    own = await client.post(
        "/me/providers", json={"provider": "groq", "api_key": "gsk_chave_do_bob_12345"}
    )
    assert own.status_code == 201
    assert own.json()["key_hint"] == "gsk…2345"

    await client.post("/auth/logout")
    await login(client, "alice@example.com")
    alice = (await client.get("/me/providers")).json()["items"]
    assert len(alice) == 1
    assert alice[0]["key_hint"] == HINT


async def test_ollama_usa_url_do_servidor(
    client: AsyncClient,
    session: AsyncSession,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(settings, "ollama_base_url", "http://ollama:11434")
    await make_user(session, "owner@example.com", role="owner")
    await login(client, "owner@example.com")

    created = await client.post("/me/providers", json={"provider": "ollama"})

    assert created.status_code == 201, created.text
    assert created.json()["base_url"] == "http://ollama:11434/v1"
    assert created.json()["key_hint"] is None


async def test_fallback_e_modo_offline(
    client: AsyncClient, session: AsyncSession, monkeypatch: pytest.MonkeyPatch
) -> None:
    await make_user(session, "owner@example.com", role="owner")
    await login(client, "owner@example.com")
    for provider in ("openrouter", "ollama", "ollama_cloud", "groq"):
        payload: dict[str, Any] = {"provider": provider}
        if provider != "ollama":
            payload["api_key"] = f"chave-{provider}-123456"
        created = await client.post("/me/providers", json=payload)
        assert created.status_code == 201, created.text

    chat = (await client.get("/me/providers/route?task=chat")).json()
    assert [item["provider"] for item in chat["chain"]] == [
        "groq",
        "ollama_cloud",
        "openrouter",
        "ollama",
    ]
    embedding = (await client.get("/me/providers/route?task=embedding")).json()
    assert [item["provider"] for item in embedding["chain"]] == ["openrouter", "ollama"]
    stt = (await client.get("/me/providers/route?task=stt")).json()
    assert [item["provider"] for item in stt["chain"]] == [
        "groq",
        "ollama_cloud",
        "openrouter",
    ]
    tts = (await client.get("/me/providers/route?task=tts")).json()
    assert [item["provider"] for item in tts["chain"]] == [
        "ollama_cloud",
        "openrouter",
    ]

    monkeypatch.setattr(settings, "offline_mode", True)
    offline = (await client.get("/me/providers/route?task=chat")).json()
    assert [item["provider"] for item in offline["chain"]] == ["ollama"]
    assert offline["offline_mode"] is True
    assert (await client.get("/me/providers")).json()["offline_mode"] is True


async def test_cadeia_respeita_o_provedor_escolhido_no_onboarding(
    client: AsyncClient, session: AsyncSession
) -> None:
    await make_user(session, "owner@example.com", role="owner")
    await login(client, "owner@example.com")
    for provider in ("openrouter", "ollama_cloud", "groq"):
        created = await client.post(
            "/me/providers",
            json={"provider": provider, "api_key": f"chave-{provider}-123456"},
        )
        assert created.status_code == 201, created.text

    onboarding = await client.post(
        "/me/onboarding",
        json={
            "ui_language": "pt-BR",
            "study_languages": ["ja-JP"],
            "level_band": "A1_A2",
            "program_source": "topics",
            "program_topics": ["travel"],
            "inference_provider": "openrouter",
            "inference_fallbacks": ["groq"],
        },
    )
    assert onboarding.status_code == 200, onboarding.text

    chain = (await client.get("/me/providers/route?task=chat")).json()
    assert [item["provider"] for item in chain["chain"]] == [
        "openrouter",
        "groq",
        "ollama_cloud",
    ]


async def test_modelo_escolhido_no_onboarding_aplica_na_credencial(
    client: AsyncClient, session: AsyncSession
) -> None:
    await make_user(session, "owner@example.com", role="owner")
    await login(client, "owner@example.com")
    created = await client.post(
        "/me/providers",
        json={"provider": "groq", "api_key": "gsk_chave_do_bob_12345"},
    )
    assert created.status_code == 201, created.text

    onboarding = await client.post(
        "/me/onboarding",
        json={
            "ui_language": "pt-BR",
            "study_languages": ["ja-JP"],
            "level_band": "A1_A2",
            "program_source": "topics",
            "program_topics": ["travel"],
            "inference_provider": "groq",
            "inference_model": "llama-3.3-70b-versatile",
        },
    )
    assert onboarding.status_code == 200, onboarding.text

    providers = (await client.get("/me/providers")).json()
    groq = next(item for item in providers["items"] if item["provider"] == "groq")
    assert groq["model"] == "llama-3.3-70b-versatile"


@pytest.mark.parametrize(
    ("status_code", "expected"),
    [
        (200, "ok"),
        (401, "invalid_key"),
        (403, "invalid_key"),
        (429, "quota"),
        (503, "provider_error"),
    ],
)
async def test_teste_de_conexao(
    client: AsyncClient,
    session: AsyncSession,
    monkeypatch: pytest.MonkeyPatch,
    status_code: int,
    expected: str,
) -> None:
    await make_user(session, "owner@example.com", role="owner")
    await login(client, "owner@example.com")
    await client.post("/me/providers", json={"provider": "groq", "api_key": SECRET})

    def handler(request: httpx.Request) -> httpx.Response:
        assert request.headers["Authorization"] == f"Bearer {SECRET}"
        assert b"ping" in request.content
        return httpx.Response(status_code, json={"error": "detalhe que nao deve vazar"})

    real_client = httpx.AsyncClient

    def fake_client(*args: Any, **kwargs: Any) -> httpx.AsyncClient:
        return real_client(transport=httpx.MockTransport(handler), timeout=5.0)

    monkeypatch.setattr(provider_client.httpx, "AsyncClient", fake_client)

    response = await client.post("/me/providers/groq/test")
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["ok"] is (status_code == 200)
    assert data["status"] == expected
    assert SECRET not in response.text
    assert "detalhe que nao deve vazar" not in response.text

    listed = (await client.get("/me/providers")).json()["items"][0]
    assert listed["last_tested_at"] is not None
    assert (listed["last_error"] is None) is (status_code == 200)


async def test_timeout_nao_vaza_chave(
    client: AsyncClient, session: AsyncSession, monkeypatch: pytest.MonkeyPatch
) -> None:
    await make_user(session, "owner@example.com", role="owner")
    await login(client, "owner@example.com")
    await client.post("/me/providers", json={"provider": "groq", "api_key": SECRET})

    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectTimeout("timeout")

    real_client = httpx.AsyncClient

    def fake_client(*args: Any, **kwargs: Any) -> httpx.AsyncClient:
        return real_client(transport=httpx.MockTransport(handler), timeout=5.0)

    monkeypatch.setattr(provider_client.httpx, "AsyncClient", fake_client)

    response = await client.post("/me/providers/groq/test")

    assert response.status_code == 200
    assert response.json()["status"] == "network"
    assert SECRET not in response.text


async def test_export_e_exclusao_apagam_credenciais(
    client: AsyncClient, session: AsyncSession
) -> None:
    await make_user(session, "alice@example.com", role="owner")
    await login(client, "alice@example.com")
    await client.post("/me/providers", json={"provider": "groq", "api_key": SECRET})

    exported = await client.get("/me/export")
    assert exported.status_code == 200
    body = exported.json()
    assert body["provider_credentials"][0]["key_hint"] == HINT
    assert SECRET not in exported.text
    assert "api_key_encrypted" not in exported.text

    deleted = await client.request("DELETE", "/me", json={"password": PASSWORD})
    assert deleted.status_code == 204
    remaining = await session.execute(text("SELECT COUNT(*) FROM provider_credentials"))
    assert remaining.scalar_one() == 0
