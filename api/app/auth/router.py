"""Rotas de autenticação: login, refresh, logout, convite e cadastro."""

from __future__ import annotations

from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Cookie, HTTPException, Request, Response, status
from sqlalchemy import select

from ..config import settings
from ..models import AuthSession, Invite, User
from ..models.base import utcnow
from ..security.limits import login_limiter
from ..security.passwords import burn_time, hash_password, needs_rehash, verify_password
from ..security.tokens import create_access_token, hash_token, new_refresh_token
from .cookies import REFRESH_COOKIE, clear_auth_cookies, set_auth_cookies
from .deps import SessionDep
from .schemas import InvitePreview, LoginIn, RegisterIn, UserOut

router = APIRouter(prefix="/auth", tags=["auth"])


def _client_key(request: Request, email: str) -> str:
    host = request.client.host if request.client else "desconhecido"
    return f"{host}:{email}"


def _client_ip(request: Request) -> str | None:
    return request.client.host if request.client else None


async def _start_session(
    session: SessionDep, user: User, request: Request, response: Response
) -> None:
    raw_refresh = new_refresh_token()
    session.add(
        AuthSession(
            user_id=user.id,
            token_hash=hash_token(raw_refresh),
            expires_at=utcnow() + timedelta(days=settings.refresh_token_ttl_days),
            user_agent=(request.headers.get("user-agent") or "")[:255] or None,
            ip=_client_ip(request),
        )
    )
    user.last_login_at = utcnow()
    await session.commit()
    set_auth_cookies(response, create_access_token(user.id, user.role), raw_refresh)


def _mask_email(email: str) -> str:
    local, _, domain = email.partition("@")
    visible = local[:1] or "*"
    return f"{visible}{'*' * 3}@{domain}"


@router.post("/login", response_model=UserOut)
async def login(
    payload: LoginIn,
    request: Request,
    response: Response,
    session: SessionDep,
) -> User:
    email = payload.email.lower().strip()
    key = _client_key(request, email)

    if login_limiter.blocked(key):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Muitas tentativas. Aguarde alguns minutos e tente de novo.",
        )

    user = await session.scalar(select(User).where(User.email == email))
    if user is None:
        burn_time()
        login_limiter.record_failure(key)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="E-mail ou senha inválidos."
        )

    if not verify_password(user.password_hash, payload.password):
        login_limiter.record_failure(key)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="E-mail ou senha inválidos."
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Esta conta está desativada."
        )

    if needs_rehash(user.password_hash):
        user.password_hash = hash_password(payload.password)

    login_limiter.reset(key)
    await _start_session(session, user, request, response)
    return user


@router.post("/refresh", response_model=UserOut)
async def refresh(
    request: Request,
    response: Response,
    session: SessionDep,
    refresh_token: Annotated[str | None, Cookie(alias=REFRESH_COOKIE)] = None,
) -> User:
    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Sessão não encontrada."
        )

    row = await session.scalar(
        select(AuthSession)
        .where(AuthSession.token_hash == hash_token(refresh_token))
        .with_for_update()
    )
    now = utcnow()
    if row is None or row.revoked_at is not None or row.expires_at <= now:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Sessão expirada.")

    user = await session.get(User, row.user_id)
    if user is None or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Sessão inválida.")

    # Rotação: o token usado morre aqui e um novo é emitido.
    row.revoked_at = now
    await _start_session(session, user, request, response)
    return user


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(
    session: SessionDep,
    refresh_token: Annotated[str | None, Cookie(alias=REFRESH_COOKIE)] = None,
) -> Response:
    if refresh_token:
        row = await session.scalar(
            select(AuthSession).where(AuthSession.token_hash == hash_token(refresh_token))
        )
        if row is not None and row.revoked_at is None:
            row.revoked_at = utcnow()
            await session.commit()

    response = Response(status_code=status.HTTP_204_NO_CONTENT)
    clear_auth_cookies(response)
    return response


@router.get("/invite/{token}", response_model=InvitePreview)
async def preview_invite(token: str, session: SessionDep) -> InvitePreview:
    invite = await session.scalar(select(Invite).where(Invite.token_hash == hash_token(token)))
    if invite is None or invite.accepted_at is not None or invite.expires_at <= utcnow():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Convite inválido ou expirado."
        )
    return InvitePreview(
        email=_mask_email(invite.email),
        role=invite.role,
        expires_at=invite.expires_at,
    )


@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def register(
    payload: RegisterIn,
    request: Request,
    response: Response,
    session: SessionDep,
) -> User:
    invite = await session.scalar(
        select(Invite).where(Invite.token_hash == hash_token(payload.token)).with_for_update()
    )
    now = utcnow()
    if invite is None or invite.accepted_at is not None or invite.expires_at <= now:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Convite inválido ou expirado."
        )

    existing = await session.scalar(select(User).where(User.email == invite.email))
    if existing is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Esta conta já existe.")

    user = User(
        email=invite.email,
        name=payload.name.strip(),
        password_hash=hash_password(payload.password),
        role=invite.role,
        is_active=True,
    )
    session.add(user)
    await session.flush()

    invite.accepted_at = now
    invite.accepted_by = user.id
    await session.commit()

    await _start_session(session, user, request, response)
    return user
