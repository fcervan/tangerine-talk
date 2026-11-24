"""Auxiliares compartilhados pelos testes."""

from __future__ import annotations

from typing import Any

from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import User
from app.security.passwords import hash_password

PASSWORD = "senha-forte-de-teste"


async def make_user(
    session: AsyncSession,
    email: str,
    role: str = "member",
    password: str = PASSWORD,
    name: str = "Pessoa Teste",
) -> User:
    user = User(
        email=email,
        name=name,
        password_hash=hash_password(password),
        role=role,
        is_active=True,
    )
    session.add(user)
    await session.commit()
    return user


async def login(client: AsyncClient, email: str, password: str = PASSWORD) -> dict[str, Any]:
    response = await client.post("/auth/login", json={"email": email, "password": password})
    assert response.status_code == 200, response.text
    data: dict[str, Any] = response.json()
    return data


def invite_token(invite_url: str) -> str:
    return invite_url.rstrip("/").rsplit("/", 1)[-1]
