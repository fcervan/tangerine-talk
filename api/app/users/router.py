"""Rotas de perfil, membros e convites."""

from __future__ import annotations

import uuid
from datetime import timedelta

from fastapi import APIRouter, HTTPException, Response, status
from fastapi.responses import JSONResponse
from sqlalchemy import delete, func, select, update

from ..auth.cookies import clear_auth_cookies
from ..auth.deps import CurrentUser, OwnerUser, SessionDep
from ..auth.schemas import (
    DeleteMeIn,
    InviteCreated,
    InviteIn,
    InviteOut,
    MemberOut,
    MeUpdateIn,
    OnboardingIn,
    OnboardingOut,
    PasswordChangeIn,
    UserOut,
)
from ..config import settings
from ..i18n import exercise_mode
from ..mail import send_invite
from ..models import AuthSession, Invite, ProviderCredential, User, UserLessonProgress
from ..models.base import utcnow
from ..security.passwords import hash_password, verify_password
from ..security.tokens import hash_token, new_refresh_token

router = APIRouter(tags=["users"])


@router.get("/me", response_model=UserOut)
async def read_me(user: CurrentUser) -> User:
    return user


@router.patch("/me", response_model=UserOut)
async def update_me(payload: MeUpdateIn, user: CurrentUser, session: SessionDep) -> User:
    if payload.name is not None:
        user.name = payload.name.strip()
    if payload.ui_language is not None:
        user.ui_language = payload.ui_language
    if payload.settings is not None:
        user.settings = dict(payload.settings)
    await session.commit()
    return user


@router.post("/me/onboarding", response_model=OnboardingOut)
async def onboarding(
    payload: OnboardingIn, user: CurrentUser, session: SessionDep
) -> OnboardingOut:
    """Define os dois eixos de idioma, nível e meta. Pode ser refeito depois."""

    user.ui_language = payload.ui_language
    user.target_language = payload.study_languages[0]
    user.study_languages = payload.study_languages
    user.level_band = payload.level_band
    user.program_source = payload.program_source
    user.program_topics = payload.program_topics
    user.inference_provider = payload.inference_provider
    user.inference_fallbacks = payload.inference_fallbacks
    user.settings = {
        **user.settings,
        "level_band": payload.level_band,
        "daily_goal_minutes": payload.daily_goal_minutes,
        "inference_model": payload.inference_model or "",
    }
    user.onboarding_completed = True
    await session.commit()

    # O modelo escolhido no onboarding vale para a credencial do provedor principal.
    if payload.inference_model:
        row = await session.scalar(
            select(ProviderCredential).where(
                ProviderCredential.user_id == user.id,
                ProviderCredential.provider == payload.inference_provider,
            )
        )
        if row is not None:
            row.model = payload.inference_model
            await session.commit()

    data = UserOut.model_validate(user).model_dump()
    data["exercise_mode"] = exercise_mode(payload.ui_language, payload.study_languages[0])
    return OnboardingOut.model_validate(data)


@router.post("/me/password", status_code=status.HTTP_204_NO_CONTENT)
async def change_password(
    payload: PasswordChangeIn, user: CurrentUser, session: SessionDep
) -> Response:
    if not verify_password(user.password_hash, payload.current_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Senha atual incorreta."
        )

    user.password_hash = hash_password(payload.new_password)
    # Trocar a senha encerra todas as sessões — inclusive a atual.
    await session.execute(delete(AuthSession).where(AuthSession.user_id == user.id))
    await session.commit()

    response = Response(status_code=status.HTTP_204_NO_CONTENT)
    clear_auth_cookies(response)
    return response


@router.get("/me/export")
async def export_me(user: CurrentUser, session: SessionDep) -> JSONResponse:
    sessions = list(
        await session.scalars(
            select(AuthSession)
            .where(AuthSession.user_id == user.id)
            .order_by(AuthSession.created_at)
        )
    )
    credentials = list(
        await session.scalars(
            select(ProviderCredential)
            .where(ProviderCredential.user_id == user.id)
            .order_by(ProviderCredential.created_at)
        )
    )
    progress = list(
        await session.scalars(
            select(UserLessonProgress)
            .where(UserLessonProgress.user_id == user.id)
            .order_by(UserLessonProgress.completed_at)
        )
    )
    payload = {
        "exported_at": utcnow().isoformat() + "Z",
        "profile": {
            "id": str(user.id),
            "email": user.email,
            "name": user.name,
            "role": user.role,
            "ui_language": user.ui_language,
            "target_language": user.target_language,
            "study_languages": list(user.study_languages or []),
            "level_band": user.level_band,
            "program_source": user.program_source,
            "program_topics": list(user.program_topics or []),
            "onboarding_completed": user.onboarding_completed,
            "settings": user.settings,
            "created_at": user.created_at.isoformat(),
            "last_login_at": user.last_login_at.isoformat() if user.last_login_at else None,
        },
        "auth_sessions": [
            {
                "id": str(row.id),
                "created_at": row.created_at.isoformat(),
                "expires_at": row.expires_at.isoformat(),
                "revoked_at": row.revoked_at.isoformat() if row.revoked_at else None,
                "ip": row.ip,
                "user_agent": row.user_agent,
            }
            for row in sessions
        ],
        # Metadados apenas: nem a chave cifrada nem a chave em claro saem daqui.
        "provider_credentials": [
            {
                "provider": row.provider,
                "key_hint": row.key_hint,
                "base_url": row.base_url,
                "model": row.model,
                "is_active": row.is_active,
                "created_at": row.created_at.isoformat(),
                "last_tested_at": row.last_tested_at.isoformat() if row.last_tested_at else None,
            }
            for row in credentials
        ],
        "lesson_progress": [
            {
                "lesson_id": str(row.lesson_id),
                "score": row.score,
                "completed_at": row.completed_at.isoformat(),
            }
            for row in progress
        ],
    }
    return JSONResponse(
        payload,
        headers={"Content-Disposition": 'attachment; filename="tangerine-dados.json"'},
    )


@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
async def delete_me(payload: DeleteMeIn, user: CurrentUser, session: SessionDep) -> Response:
    if not verify_password(user.password_hash, payload.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Senha incorreta.")

    if user.role == "owner":
        others = await session.scalar(
            select(func.count()).select_from(User).where(User.id != user.id)
        )
        if others:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Remova os membros da instância antes de excluir a conta do owner.",
            )

    await session.execute(delete(AuthSession).where(AuthSession.user_id == user.id))
    await session.execute(delete(ProviderCredential).where(ProviderCredential.user_id == user.id))
    await session.execute(delete(UserLessonProgress).where(UserLessonProgress.user_id == user.id))
    await session.execute(delete(Invite).where(Invite.created_by == user.id))
    await session.execute(
        update(Invite).where(Invite.accepted_by == user.id).values(accepted_by=None)
    )
    await session.delete(user)
    await session.commit()

    response = Response(status_code=status.HTTP_204_NO_CONTENT)
    clear_auth_cookies(response)
    return response


@router.get("/members", response_model=list[MemberOut])
async def list_members(owner: OwnerUser, session: SessionDep) -> list[User]:
    return list(await session.scalars(select(User).order_by(User.created_at)))


@router.post("/invites", response_model=InviteCreated, status_code=status.HTTP_201_CREATED)
async def create_invite(
    payload: InviteIn,
    owner: OwnerUser,
    session: SessionDep,
) -> InviteCreated:
    email = payload.email.lower().strip()

    existing = await session.scalar(select(User).where(User.email == email))
    if existing is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Já existe uma conta com este e-mail.",
        )

    raw_token = new_refresh_token()
    invite = Invite(
        email=email,
        role="member",
        token_hash=hash_token(raw_token),
        expires_at=utcnow() + timedelta(days=settings.invite_ttl_days),
        created_by=owner.id,
    )
    session.add(invite)
    await session.commit()

    base = settings.public_base_url.rstrip("/")
    invite_url = f"{base}/convite/{raw_token}"
    sent = await send_invite(email, invite_url, invite.expires_at)
    return InviteCreated(
        invite=InviteOut.model_validate(invite),
        invite_url=invite_url,
        email_sent=sent,
    )


@router.get("/invites", response_model=list[InviteOut])
async def list_invites(owner: OwnerUser, session: SessionDep) -> list[Invite]:
    return list(await session.scalars(select(Invite).order_by(Invite.created_at.desc())))


@router.delete("/invites/{invite_id}", status_code=status.HTTP_204_NO_CONTENT)
async def revoke_invite(invite_id: uuid.UUID, owner: OwnerUser, session: SessionDep) -> Response:
    invite = await session.get(Invite, invite_id)
    if invite is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Convite não encontrado.")
    await session.delete(invite)
    await session.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
