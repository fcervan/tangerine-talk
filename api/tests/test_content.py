"""Trilha, conteúdo versionado, progresso e glossas por idioma da interface."""

from __future__ import annotations

from typing import Any

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.content.seed import seed_content

from .helpers import login, make_user


async def prepared_user(
    session: AsyncSession,
    email: str = "aluno@example.com",
    ui_language: str = "pt-BR",
) -> None:
    user = await make_user(session, email, role="owner")
    user.ui_language = ui_language
    user.target_language = "es"
    user.settings = {"level": "A1"}
    user.onboarding_completed = True
    await session.commit()


async def setup(client: AsyncClient, session: AsyncSession, ui_language: str = "pt-BR") -> None:
    await seed_content(session, target_language="es")
    await prepared_user(session, ui_language=ui_language)
    await login(client, "aluno@example.com")


async def first_units(client: AsyncClient) -> list[dict[str, Any]]:
    response = await client.get("/curriculum")
    assert response.status_code == 200, response.text
    return response.json()["units"]


async def test_seed_e_idempotente(session: AsyncSession) -> None:
    first = await seed_content(session, target_language="es")
    assert first == {"units": 10, "lessons": 18, "items": 65, "exercises": 48, "decks": 2}
    second = await seed_content(session, target_language="es")
    assert not any(second.values())


async def test_idiomas_com_conteudo(client: AsyncClient, session: AsyncSession) -> None:
    await setup(client, session)
    response = await client.get("/curriculum/languages")
    assert response.status_code == 200, response.text
    assert response.json() == {"languages": ["es"]}


async def test_trilha_respeita_pre_requisito(client: AsyncClient, session: AsyncSession) -> None:
    await setup(client, session)
    units = await first_units(client)

    # Primeiras 2 unidades (A1): saudacoes, numeros-1-10
    assert [unit["slug"] for unit in units[:2]] == ["saudacoes", "numeros-1-10"]
    assert [unit["status"] for unit in units[:2]] == ["available", "locked"]
    # Primeira unidade tem 2 lições (primeiras-saudacoes, agradecimentos)
    assert len(units[0]["lessons"]) == 2
    assert [lesson["status"] for lesson in units[0]["lessons"]] == [
        "available",
        "available",
    ]
    assert units[0]["lessons"][0]["exercise_count"] == 4  # 4 exercícios na primeira lição
    locked_lesson = units[1]["lessons"][0]["id"]

    detail = await client.get(f"/curriculum/lessons/{locked_lesson}")
    assert detail.status_code == 403
    blocked = await client.post(f"/curriculum/lessons/{locked_lesson}/complete", json={})
    assert blocked.status_code == 403


async def test_concluir_licoes_desbloqueia_e_xp_nao_duplica(
    client: AsyncClient, session: AsyncSession
) -> None:
    await setup(client, session)
    units = await first_units(client)
    lesson_ids = [lesson["id"] for lesson in units[0]["lessons"]]

    for lesson_id in lesson_ids:
        done = await client.post(f"/curriculum/lessons/{lesson_id}/complete", json={"score": 90})
        assert done.status_code == 200, done.text
        assert done.json()["xp_earned"] == 10

    units = await first_units(client)
    # Apenas as duas primeiras unidades (A1) são afetadas pelo progresso
    assert units[0]["status"] == "completed"
    assert units[1]["status"] == "available"
    assert all(lesson["status"] == "completed" for lesson in units[0]["lessons"])

    repeat = await client.post(f"/curriculum/lessons/{lesson_ids[0]}/complete", json={})
    assert repeat.json()["status"] == "already_completed"
    assert repeat.json()["xp_earned"] == 0


@pytest.mark.parametrize(
    ("ui_language", "expected"),
    [
        ("pt-BR", "Olá"),
        ("en-US", "Hello"),
        ("fr-FR", "Olá"),  # sem dicionário: cai para pt-BR, nunca inglês
    ],
)
async def test_glosa_segue_idioma_da_interface(
    client: AsyncClient, session: AsyncSession, ui_language: str, expected: str
) -> None:
    await setup(client, session, ui_language=ui_language)
    units = await first_units(client)
    lesson_id = units[0]["lessons"][0]["id"]

    detail = await client.get(f"/curriculum/lessons/{lesson_id}")
    assert detail.status_code == 200, detail.text
    body = detail.json()
    flashcard = next(item for item in body["exercises"] if item["type"] == "flashcard")
    assert flashcard["prompt"] == "Hola"  # frase permanece no idioma alvo
    assert flashcard["answer"] == expected
    assert body["items"][0]["gloss_locale"] in {"pt-BR", "en-US"}


async def test_unidade_detalha_itens_e_decks_oficiais(
    client: AsyncClient, session: AsyncSession
) -> None:
    await setup(client, session, ui_language="en-US")
    units = await first_units(client)

    detail = await client.get(f"/curriculum/units/{units[0]['id']}")
    assert detail.status_code == 200, detail.text
    # Primeira unidade (saudacoes) tem 8 itens
    assert len(detail.json()["items"]) == 8
    assert detail.json()["items"][0]["gloss_locale"] == "en-US"

    decks = await client.get("/decks")
    assert decks.status_code == 200, decks.text
    assert decks.json()["target_language"] == "es"
    assert len(decks.json()["decks"]) == 2
    # Deck essencial A1 tem 35 itens
    assert decks.json()["decks"][0]["item_count"] == 35

    deck = await client.get(f"/decks/{decks.json()['decks'][0]['id']}")
    assert deck.status_code == 200, deck.text
    assert len(deck.json()["items"]) == 35
    # O primeiro item pode variar dependendo da ordem de inserção; verificar se "Hola" está presente
    front_texts = [item["front_text"] for item in deck.json()["items"]]
    assert "Hola" in front_texts
    hola_item = next(item for item in deck.json()["items"] if item["front_text"] == "Hola")
    assert hola_item["gloss"] == "Hello"


async def test_progresso_e_isolado_por_usuario(client: AsyncClient, session: AsyncSession) -> None:
    await seed_content(session, target_language="es")
    await prepared_user(session, "um@example.com")
    await prepared_user(session, "dois@example.com")
    await login(client, "um@example.com")

    units = await first_units(client)
    lesson_id = units[0]["lessons"][0]["id"]
    done = await client.post(f"/curriculum/lessons/{lesson_id}/complete", json={})
    assert done.status_code == 200

    await client.post("/auth/logout")
    await login(client, "dois@example.com")
    units = await first_units(client)
    assert units[0]["lessons"][0]["status"] == "available"
    assert units[0]["status"] == "available"


async def test_sem_idioma_alvo_e_sem_sessao(client: AsyncClient, session: AsyncSession) -> None:
    assert (await client.get("/curriculum")).status_code == 401

    user = await make_user(session, "sem-alvo@example.com", role="owner")
    user.onboarding_completed = True
    await session.commit()
    await login(client, "sem-alvo@example.com")

    response = await client.get("/curriculum")
    assert response.status_code == 400
    assert "idioma estudado" in response.json()["detail"].lower()


async def test_exportacao_inclui_progresso_sem_dados_de_outro_usuario(
    client: AsyncClient, session: AsyncSession
) -> None:
    await setup(client, session)
    units = await first_units(client)
    lesson_id = units[0]["lessons"][0]["id"]
    await client.post(f"/curriculum/lessons/{lesson_id}/complete", json={"score": 80})

    exported = await client.get("/me/export")
    assert exported.status_code == 200, exported.text
    progress = exported.json()["lesson_progress"]
    assert len(progress) == 1
    assert progress[0]["lesson_id"] == lesson_id
    assert progress[0]["score"] == 80
