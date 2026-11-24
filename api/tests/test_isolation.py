"""Isolamento entre usuários: A não acessa nem administra os dados de B."""

from __future__ import annotations

from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from .helpers import PASSWORD, login, make_user


async def test_membro_nao_lista_membros(client: AsyncClient, session: AsyncSession) -> None:
    await make_user(session, "owner@example.com", role="owner")
    await make_user(session, "membro@example.com")
    await login(client, "membro@example.com")

    response = await client.get("/members")

    assert response.status_code == 403


async def test_membro_nao_cria_convite(client: AsyncClient, session: AsyncSession) -> None:
    await make_user(session, "owner@example.com", role="owner")
    await make_user(session, "membro@example.com")
    await login(client, "membro@example.com")

    response = await client.post("/invites", json={"email": "intruso@example.com"})

    assert response.status_code == 403


async def test_membro_nao_revoga_convite(client: AsyncClient, session: AsyncSession) -> None:
    await make_user(session, "owner@example.com", role="owner")
    await make_user(session, "membro@example.com")

    await login(client, "owner@example.com")
    created = await client.post("/invites", json={"email": "alguem@example.com"})
    invite_id = created.json()["invite"]["id"]

    await client.post("/auth/logout")
    await login(client, "membro@example.com")

    response = await client.delete(f"/invites/{invite_id}")

    assert response.status_code == 403


async def test_me_nunca_expoe_outro_usuario(
    client: AsyncClient, session: AsyncSession
) -> None:
    await make_user(session, "owner@example.com", role="owner", name="Dona")
    membro = await make_user(session, "membro@example.com", name="Membro")
    await login(client, "membro@example.com")

    me = await client.get("/me")

    assert me.json()["id"] == str(membro.id)
    assert me.json()["name"] == "Membro"


async def test_owner_nao_exclui_conta_com_membros(
    client: AsyncClient, session: AsyncSession
) -> None:
    await make_user(session, "owner@example.com", role="owner")
    await make_user(session, "membro@example.com")
    await login(client, "owner@example.com")

    response = await client.request("DELETE", "/me", json={"password": PASSWORD})

    assert response.status_code == 409


async def test_membros_so_aparecem_para_o_owner(
    client: AsyncClient, session: AsyncSession
) -> None:
    await make_user(session, "owner@example.com", role="owner")
    await make_user(session, "membro@example.com")
    await login(client, "owner@example.com")

    response = await client.get("/members")

    assert response.status_code == 200
    emails = {row["email"] for row in response.json()}
    assert emails == {"owner@example.com", "membro@example.com"}
