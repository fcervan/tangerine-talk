"""Comandos de administração da instância.

Não existe usuário padrão nem senha padrão: o owner é criado por este comando,
com senha digitada ou gerada na hora.

    python -m app.cli create-owner --email voce@exemplo.com --name "Seu Nome"
    python -m app.cli invite --email pessoa@exemplo.com
    python -m app.cli seed-content
"""

from __future__ import annotations

import argparse
import asyncio
import getpass
import secrets
import sys
from datetime import timedelta

from sqlalchemy import select

from .config import settings
from .content.seed import seed_content
from .db import dispose_engine, get_session_factory
from .models import Invite, User
from .models.base import utcnow
from .security.passwords import hash_password
from .security.tokens import hash_token, new_refresh_token

MIN_PASSWORD_LENGTH = 12


def _ask_password() -> str:
    while True:
        first = getpass.getpass("Senha do owner: ")
        if len(first) < MIN_PASSWORD_LENGTH:
            print(f"A senha precisa ter ao menos {MIN_PASSWORD_LENGTH} caracteres.")
            continue
        second = getpass.getpass("Repita a senha: ")
        if first != second:
            print("As senhas não conferem.")
            continue
        return first


async def _create_owner(email: str, name: str, password: str, force: bool) -> int:
    settings.ensure_secret_key()
    async with get_session_factory()() as session:
        current = await session.scalar(select(User).where(User.role == "owner"))
        if current is not None and not force:
            print(
                f"Já existe um owner ({current.email}). Use --force para criar outro.",
                file=sys.stderr,
            )
            return 1

        email = email.lower().strip()
        if await session.scalar(select(User).where(User.email == email)) is not None:
            print("Este e-mail já está cadastrado.", file=sys.stderr)
            return 1

        user = User(
            email=email,
            name=name.strip(),
            password_hash=hash_password(password),
            role="owner",
            is_active=True,
        )
        session.add(user)
        await session.commit()
        print(f"Owner criado: {user.email} (id {user.id})")
        return 0


async def _invite(email: str) -> int:
    async with get_session_factory()() as session:
        owner = await session.scalar(select(User).where(User.role == "owner"))
        if owner is None:
            print("Nenhum owner existe ainda. Rode create-owner primeiro.", file=sys.stderr)
            return 1

        email = email.lower().strip()
        if await session.scalar(select(User).where(User.email == email)) is not None:
            print("Este e-mail já está cadastrado.", file=sys.stderr)
            return 1

        raw = new_refresh_token()
        invite = Invite(
            email=email,
            role="member",
            token_hash=hash_token(raw),
            expires_at=utcnow() + timedelta(days=settings.invite_ttl_days),
            created_by=owner.id,
        )
        session.add(invite)
        await session.commit()

        base = settings.public_base_url.rstrip("/")
        expires = invite.expires_at.strftime("%d/%m/%Y %H:%M")
        print(f"Convite para {email} (expira em {expires} UTC):")
        print(f"{base}/convite/{raw}")
        return 0


async def _seed_content() -> int:
    async with get_session_factory()() as session:
        counts = await seed_content(session)
    if not any(counts.values()):
        print("Conteúdo oficial já estava carregado; nada foi alterado.")
    else:
        print("Conteúdo criado: " + ", ".join(f"{key}={value}" for key, value in counts.items()))
    return 0


def main() -> None:
    parser = argparse.ArgumentParser(prog="python -m app.cli")
    sub = parser.add_subparsers(dest="command", required=True)

    owner = sub.add_parser("create-owner", help="cria o primeiro usuário (owner)")
    owner.add_argument("--email", required=True)
    owner.add_argument("--name", required=True)
    owner.add_argument(
        "--generate",
        action="store_true",
        help="gera uma senha aleatória e a exibe uma única vez",
    )
    owner.add_argument("--force", action="store_true", help="permite mais de um owner")

    invite = sub.add_parser("invite", help="gera um convite por e-mail")
    invite.add_argument("--email", required=True)

    sub.add_parser("seed-content", help="carrega o currículo oficial (idempotente)")

    args = parser.parse_args()

    async def run() -> int:
        try:
            if args.command == "create-owner":
                password = secrets.token_urlsafe(18) if args.generate else _ask_password()
                if args.generate:
                    print(f"Senha gerada para {args.email}: {password}")
                    print("Guarde agora — ela não será exibida de novo.")
                return await _create_owner(args.email, args.name, password, args.force)
            if args.command == "invite":
                return await _invite(args.email)
            if args.command == "seed-content":
                return await _seed_content()
            return 2
        finally:
            await dispose_engine()

    raise SystemExit(asyncio.run(run()))


if __name__ == "__main__":
    main()
