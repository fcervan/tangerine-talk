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


async def test_onboarding_salva_os_dois_eixos(
    client: AsyncClient, session: AsyncSession
) -> None:
    await make_user(session, "pessoa@example.com")
    await login(client, "pessoa@example.com")

    response = await client.post(
        "/me/onboarding",
        json={
            "ui_language": "en-us",
            "target_language": "ja-JP",
            "level": "A2",
            "daily_goal_minutes": 25,
        },
    )

    assert response.status_code == 200, response.text
    data: dict[str, Any] = response.json()
    assert data["ui_language"] == "en-US"
    assert data["target_language"] == "ja-JP"
    assert data["onboarding_completed"] is True
    assert data["exercise_mode"] == "bilingual"
    assert data["settings"]["level"] == "A2"
    assert data["settings"]["daily_goal_minutes"] == 25

    user = await session.scalar(select(User).where(User.email == "pessoa@example.com"))
    assert user is not None
    assert user.target_language == "ja-JP"


async def test_par_igual_gera_deck_monolingual(
    client: AsyncClient, session: AsyncSession
) -> None:
    await make_user(session, "mono@example.com")
    await login(client, "mono@example.com")

    response = await client.post(
        "/me/onboarding",
        json={
            "ui_language": "en-US",
            "target_language": "en-GB",
            "level": "B1",
        },
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
        json={
            "ui_language": "pt-BR",
            "target_language": "ja-JP",
            "level": "A1",
        },
    )

    response = await client.patch("/me", json={"ui_language": "en-us"})

    assert response.status_code == 200, response.text
    data: dict[str, Any] = response.json()
    assert data["ui_language"] == "en-US"
    assert data["target_language"] == "ja-JP"
    assert data["onboarding_completed"] is True


async def test_locale_invalido_e_rejeitado(
    client: AsyncClient, session: AsyncSession
) -> None:
    await make_user(session, "invalido@example.com")
    await login(client, "invalido@example.com")

    assert (await client.patch("/me", json={"ui_language": "pt_br"})).status_code == 422
    assert (
        await client.post(
            "/me/onboarding",
            json={
                "ui_language": "pt-BR",
                "target_language": "qualquer-coisa",
                "level": "A1",
            },
        )
    ).status_code == 422


async def test_export_inclui_os_novos_campos(
    client: AsyncClient, session: AsyncSession
) -> None:
    await make_user(session, "export@example.com")
    await login(client, "export@example.com")
    await client.post(
        "/me/onboarding",
        json={"ui_language": "pt-BR", "target_language": "de-DE", "level": "A1"},
    )

    response = await client.get("/me/export")

    assert response.status_code == 200, response.text
    profile = response.json()["profile"]
    assert profile["ui_language"] == "pt-BR"
    assert profile["target_language"] == "de-DE"
    assert profile["onboarding_completed"] is True


async def test_onboarding_de_um_usuario_nao_altera_o_outro(
    client: AsyncClient, session: AsyncSession
) -> None:
    await make_user(session, "um@example.com")
    await make_user(session, "dois@example.com")
    await login(client, "um@example.com")
    await client.post(
        "/me/onboarding",
        json={"ui_language": "pt-BR", "target_language": "ko-KR", "level": "A1"},
    )
    client.cookies.clear()
    await login(client, "dois@example.com")

    me = await client.get("/me")

    assert me.status_code == 200, me.text
    assert me.json()["target_language"] is None
    assert me.json()["onboarding_completed"] is False
