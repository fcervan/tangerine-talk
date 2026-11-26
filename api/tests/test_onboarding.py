"""Onboarding: interface e idioma estudado são eixos independentes."""

from __future__ import annotations

from typing import Any

import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.i18n import base_language, exercise_mode, normalize_locale
from app.models import User

from .helpers import login, make_user


def test_normalizacao_de_locale() -> None:
    assert normalize_locale("pt-br") == "pt-BR"
    assert normalize_locale("EN-us") == "en-US"
    assert normalize_locale("zh-hans-cn") == "zh-Hans-CN"
    assert normalize_locale("es-419") == "es-419"
    with pytest.raises(ValueError):
        normalize_locale("pt_br")
    with pytest.raises(ValueError):
        normalize_locale("ingles")


def test_modo_de_exercicio() -> None:
    assert exercise_mode("pt-BR", "ja-JP") == "bilingual"
    assert exercise_mode("en-US", "pt-BR") == "bilingual"
    assert exercise_mode("pt-BR", "pt-PT") == "monolingual"
    assert base_language("zh-Hans-CN") == "zh"


def onboarding_payload(**overrides: Any) -> dict[str, Any]:
    """Payload padrão do onboarding (campos obrigatórios + escolha de inferência)."""
    payload: dict[str, Any] = {
        "ui_language": "pt-BR",
        "study_languages": ["ja-JP"],
        "level_band": "A1_A2",
        "program_source": "topics",
        "program_topics": ["travel"],
        "daily_goal_minutes": 15,
        "inference_provider": "groq",
        "inference_fallbacks": ["ollama_cloud", "openrouter"],
    }
    payload.update(overrides)
    return payload


async def test_onboarding_salva_os_dois_eixos(client: AsyncClient, session: AsyncSession) -> None:
    await make_user(session, "pessoa@example.com")
    await login(client, "pessoa@example.com")

    response = await client.post(
        "/me/onboarding",
        json=onboarding_payload(
            ui_language="en-us",
            daily_goal_minutes=25,
        ),
    )

    assert response.status_code == 200, response.text
    data: dict[str, Any] = response.json()
    assert data["ui_language"] == "en-US"
    assert data["target_language"] == "ja-JP"
    assert data["onboarding_completed"] is True
    assert data["exercise_mode"] == "bilingual"
    assert data["settings"]["level_band"] == "A1_A2"
    assert data["settings"]["daily_goal_minutes"] == 25

    user = await session.scalar(select(User).where(User.email == "pessoa@example.com"))
    assert user is not None
    assert user.target_language == "ja-JP"


async def test_onboarding_salva_provedor_de_inferencia(
    client: AsyncClient, session: AsyncSession
) -> None:
    await make_user(session, "inferencia@example.com")
    await login(client, "inferencia@example.com")

    response = await client.post(
        "/me/onboarding",
        json=onboarding_payload(
            inference_provider="openrouter",
            inference_fallbacks=["groq", "ollama_cloud"],
            inference_model="  llama-3.3-70b-versatile  ",
        ),
    )

    assert response.status_code == 200, response.text
    data: dict[str, Any] = response.json()
    assert data["inference_provider"] == "openrouter"
    assert data["inference_fallbacks"] == ["groq", "ollama_cloud"]
    assert data["settings"]["inference_model"] == "llama-3.3-70b-versatile"

    user = await session.scalar(select(User).where(User.email == "inferencia@example.com"))
    assert user is not None
    assert user.inference_provider == "openrouter"
    assert list(user.inference_fallbacks) == ["groq", "ollama_cloud"]


async def test_fallback_nao_repete_o_provedor_principal(
    client: AsyncClient, session: AsyncSession
) -> None:
    await make_user(session, "dedup@example.com")
    await login(client, "dedup@example.com")

    response = await client.post(
        "/me/onboarding",
        json=onboarding_payload(
            inference_provider="groq",
            inference_fallbacks=["groq", "openrouter", "openrouter"],
        ),
    )

    assert response.status_code == 200, response.text
    assert response.json()["inference_fallbacks"] == ["openrouter"]


async def test_provedor_de_inferencia_desconhecido_e_rejeitado(
    client: AsyncClient, session: AsyncSession
) -> None:
    await make_user(session, "provedor@example.com")
    await login(client, "provedor@example.com")

    response = await client.post(
        "/me/onboarding",
        json=onboarding_payload(inference_provider="desconhecido"),
    )

    assert response.status_code == 422


async def test_par_igual_gera_deck_monolingual(client: AsyncClient, session: AsyncSession) -> None:
    await make_user(session, "mono@example.com")
    await login(client, "mono@example.com")

    response = await client.post(
        "/me/onboarding",
        json=onboarding_payload(
            ui_language="en-US",
            study_languages=["en-GB"],
            level_band="B1_B2",
        ),
    )

    assert response.status_code == 200, response.text
    assert response.json()["exercise_mode"] == "monolingual"
    assert response.json()["settings"]["daily_goal_minutes"] == 15


async def test_patch_me_troca_apenas_a_interface(
    client: AsyncClient, session: AsyncSession
) -> None:
    await make_user(session, "troca@example.com")
    await login(client, "troca@example.com")
    await client.post(
        "/me/onboarding",
        json=onboarding_payload(level_band="NONE"),
    )

    response = await client.patch("/me", json={"ui_language": "en-us"})

    assert response.status_code == 200, response.text
    data: dict[str, Any] = response.json()
    assert data["ui_language"] == "en-US"
    assert data["target_language"] == "ja-JP"
    assert data["onboarding_completed"] is True


async def test_locale_invalido_e_rejeitado(client: AsyncClient, session: AsyncSession) -> None:
    await make_user(session, "invalido@example.com")
    await login(client, "invalido@example.com")

    assert (await client.patch("/me", json={"ui_language": "pt_br"})).status_code == 422
    assert (
        await client.post(
            "/me/onboarding",
            json=onboarding_payload(study_languages=["qualquer-coisa"]),
        )
    ).status_code == 422


async def test_export_inclui_os_novos_campos(client: AsyncClient, session: AsyncSession) -> None:
    await make_user(session, "export@example.com")
    await login(client, "export@example.com")
    await client.post(
        "/me/onboarding",
        json=onboarding_payload(study_languages=["de-DE"], level_band="NONE"),
    )

    response = await client.get("/me/export")

    assert response.status_code == 200, response.text
    profile = response.json()["profile"]
    assert profile["ui_language"] == "pt-BR"
    assert profile["target_language"] == "de-DE"
    assert profile["onboarding_completed"] is True
    assert profile["inference_provider"] == "groq"


async def test_onboarding_de_um_usuario_nao_altera_o_outro(
    client: AsyncClient, session: AsyncSession
) -> None:
    await make_user(session, "um@example.com")
    await make_user(session, "dois@example.com")
    await login(client, "um@example.com")
    await client.post(
        "/me/onboarding",
        json=onboarding_payload(study_languages=["ko-KR"], level_band="NONE"),
    )
    client.cookies.clear()
    await login(client, "dois@example.com")

    me = await client.get("/me")

    assert me.status_code == 200, me.text
    assert me.json()["target_language"] is None
    assert me.json()["onboarding_completed"] is False
    assert me.json()["inference_provider"] is None
