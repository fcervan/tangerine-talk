"""Fluxo de autenticação: login, cookies, refresh, convite e senha."""

from __future__ import annotations

from httpx import AsyncClient
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import AuthSession, User
from app.security.tokens import hash_token

from .helpers import PASSWORD, invite_token, login, make_user


async def test_login_define_cookies_httponly(client: AsyncClient, session: AsyncSession) -> None:
    await make_user(session, "owner@example.com", role="owner")

    response = await client.post(
        "/auth/login", json={"email": "owner@example.com", "password": PASSWORD}
    )

    assert response.status_code == 200
    cookies = response.headers.get_list("set-cookie")
    assert any("tt_access=" in value and "HttpOnly" in value for value in cookies)
    assert any("tt_refresh=" in value and "HttpOnly" in value for value in cookies)
    assert all("SameSite=lax" in value for value in cookies)
    assert "password_hash" not in response.text


async def test_login_senha_errada_recusa(client: AsyncClient, session: AsyncSession) -> None:
    await make_user(session, "owner@example.com", role="owner")

    response = await client.post(
        "/auth/login", json={"email": "owner@example.com", "password": "senha-errada"}
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "E-mail ou senha inválidos."


async def test_login_email_inexistente_recusa(client: AsyncClient) -> None:
    response = await client.post(
        "/auth/login", json={"email": "ninguem@example.com", "password": "qualquer-senha"}
    )
    assert response.status_code == 401


async def test_me_sem_sessao_recusa(client: AsyncClient) -> None:
    assert (await client.get("/me")).status_code == 401


async def test_me_retorna_usuario_logado(client: AsyncClient, session: AsyncSession) -> None:
    user = await make_user(session, "owner@example.com", role="owner")
    await login(client, "owner@example.com")

    response = await client.get("/me")

    assert response.status_code == 200
    body = response.json()
    assert body["id"] == str(user.id)
    assert body["email"] == "owner@example.com"
    assert body["role"] == "owner"


async def test_refresh_rotaciona_e_revoga_token_antigo(
    client: AsyncClient, session: AsyncSession
) -> None:
    await make_user(session, "owner@example.com", role="owner")
    await login(client, "owner@example.com")
    old_token = client.cookies.get("tt_refresh")
    assert old_token is not None

    response = await client.post("/auth/refresh")
    assert response.status_code == 200

    new_token = client.cookies.get("tt_refresh")
    assert new_token is not None
    assert new_token != old_token

    revoked = await session.scalar(
        select(AuthSession).where(AuthSession.token_hash == hash_token(old_token))
    )
    assert revoked is not None
    assert revoked.revoked_at is not None

    client.cookies.clear()
    client.cookies.set("tt_refresh", old_token)
    reused = await client.post("/auth/refresh")
    assert reused.status_code == 401


async def test_logout_revoga_sessao(client: AsyncClient, session: AsyncSession) -> None:
    await make_user(session, "owner@example.com", role="owner")
    await login(client, "owner@example.com")
    token = client.cookies.get("tt_refresh")
    assert token is not None

    response = await client.post("/auth/logout")
    assert response.status_code == 204

    row = await session.scalar(
        select(AuthSession).where(AuthSession.token_hash == hash_token(token))
    )
    assert row is not None and row.revoked_at is not None
    assert (await client.post("/auth/refresh")).status_code == 401


async def test_convite_cria_membro(client: AsyncClient, session: AsyncSession) -> None:
    await make_user(session, "owner@example.com", role="owner")
    await login(client, "owner@example.com")

    created = await client.post("/invites", json={"email": "membro@example.com"})
    assert created.status_code == 201
    payload = created.json()
    assert payload["email_sent"] is False
    assert "/convite/" in payload["invite_url"]

    token = invite_token(payload["invite_url"])

    preview = await client.get(f"/auth/invite/{token}")
    assert preview.status_code == 200
    assert preview.json()["email"] == "m***@example.com"

    registered = await client.post(
        "/auth/register",
        json={"token": token, "name": "Membro", "password": "outra-senha-muito-forte"},
    )
    assert registered.status_code == 201
    assert registered.json()["email"] == "membro@example.com"
    assert registered.json()["role"] == "member"

    me = await client.get("/me")
    assert me.json()["email"] == "membro@example.com"


async def test_convite_nao_pode_ser_reutilizado(client: AsyncClient, session: AsyncSession) -> None:
    await make_user(session, "owner@example.com", role="owner")
    await login(client, "owner@example.com")

    created = await client.post("/invites", json={"email": "membro@example.com"})
    token = invite_token(created.json()["invite_url"])

    first = await client.post(
        "/auth/register",
        json={"token": token, "name": "Membro", "password": "outra-senha-muito-forte"},
    )
    assert first.status_code == 201

    second = await client.post(
        "/auth/register",
        json={"token": token, "name": "Outro", "password": "mais-uma-senha-forte"},
    )
    assert second.status_code == 400


async def test_convite_para_email_ja_cadastrado_falha(
    client: AsyncClient, session: AsyncSession
) -> None:
    await make_user(session, "owner@example.com", role="owner")
    await make_user(session, "membro@example.com")
    await login(client, "owner@example.com")

    response = await client.post("/invites", json={"email": "membro@example.com"})

    assert response.status_code == 409


async def test_troca_de_senha_encerra_sessoes(client: AsyncClient, session: AsyncSession) -> None:
    await make_user(session, "owner@example.com", role="owner")
    await login(client, "owner@example.com")

    changed = await client.post(
        "/me/password",
        json={"current_password": PASSWORD, "new_password": "nova-senha-muito-forte"},
    )
    assert changed.status_code == 204

    assert (await client.post("/auth/refresh")).status_code == 401

    old = await client.post(
        "/auth/login", json={"email": "owner@example.com", "password": PASSWORD}
    )
    assert old.status_code == 401

    new = await client.post(
        "/auth/login",
        json={"email": "owner@example.com", "password": "nova-senha-muito-forte"},
    )
    assert new.status_code == 200


async def test_exporta_dados_proprios_sem_segredos(
    client: AsyncClient, session: AsyncSession
) -> None:
    await make_user(session, "owner@example.com", role="owner")
    await make_user(session, "membro@example.com")
    await login(client, "membro@example.com")

    response = await client.get("/me/export")

    assert response.status_code == 200
    body = response.json()
    assert body["profile"]["email"] == "membro@example.com"
    assert "password_hash" not in response.text
    assert "token_hash" not in response.text


async def test_cadastro_publico_cria_conta_e_sessao(
    client: AsyncClient, session: AsyncSession
) -> None:
    response = await client.post(
        "/auth/register-public",
        json={
            "name": "Novo Usuário",
            "email": "novo@example.com",
            "password": "senha-publica-muito-forte",
        },
    )

    assert response.status_code == 201, response.text
    body = response.json()
    assert body["email"] == "novo@example.com"
    assert body["role"] == "member"
    assert body["onboarding_completed"] is False

    user = await session.scalar(select(User).where(User.email == "novo@example.com"))
    assert user is not None

    me = await client.get("/me")
    assert me.status_code == 200
    assert me.json()["email"] == "novo@example.com"


async def test_cadastro_publico_recusa_email_duplicado(
    client: AsyncClient, session: AsyncSession
) -> None:
    await make_user(session, "membro@example.com")

    response = await client.post(
        "/auth/register-public",
        json={
            "name": "Outro",
            "email": "membro@example.com",
            "password": "senha-publica-muito-forte",
        },
    )

    assert response.status_code == 409


async def test_exclui_propria_conta(client: AsyncClient, session: AsyncSession) -> None:
    user = await make_user(session, "membro@example.com")
    await login(client, "membro@example.com")

    response = await client.request("DELETE", "/me", json={"password": PASSWORD})

    assert response.status_code == 204
    # Conta direto no banco: a sessão do teste ainda tem o objeto em cache.
    restantes = await session.scalar(
        select(func.count()).select_from(User).where(User.id == user.id)
    )
    assert restantes == 0

    denied = await client.post(
        "/auth/login", json={"email": "membro@example.com", "password": PASSWORD}
    )
    assert denied.status_code == 401
