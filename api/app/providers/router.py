"""Rotas de BYOK. Escopo sempre limitado ao usuário autenticado."""

from __future__ import annotations

import uuid
from typing import Annotated

from fastapi import APIRouter, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..auth.deps import CurrentUser, SessionDep
from ..config import settings
from ..models import ProviderCredential
from ..models.base import utcnow
from ..security.keys import encrypt_secret, mask_secret
from .catalog import (
    FALLBACK_ORDER,
    ProviderSlug,
    ProviderSpec,
    TaskName,
    get_spec,
    public_catalog,
)
from .client import resolve_chain, test_connection
from .schemas import (
    ProviderIn,
    ProviderListOut,
    ProviderOut,
    ProviderTestOut,
    ProviderUpdateIn,
    RouteItem,
    RouteOut,
    validate_fields,
)

router = APIRouter(prefix="/me/providers", tags=["providers"])


async def _find(
    session: AsyncSession, user_id: uuid.UUID, provider: str
) -> ProviderCredential | None:
    return await session.scalar(
        select(ProviderCredential).where(
            ProviderCredential.user_id == user_id,
            ProviderCredential.provider == provider,
        )
    )


def _default_base_url(spec: ProviderSpec) -> str:
    """O Ollama local pode vir da configuração do servidor, não do env do usuário."""
    if spec.slug == "ollama" and settings.ollama_base_url:
        url = settings.ollama_base_url.rstrip("/")
        return url if url.endswith("/v1") else f"{url}/v1"
    return spec.default_base_url


def _label(provider: str) -> str:
    spec = get_spec(provider)
    return spec.label if spec else provider


def _serialize(row: ProviderCredential) -> ProviderOut:
    spec = get_spec(row.provider)
    return ProviderOut(
        id=row.id,
        provider=row.provider,
        label=_label(row.provider),
        key_hint=row.key_hint,
        base_url=row.base_url,
        model=row.model,
        capabilities=sorted(spec.capabilities) if spec else [],
        is_active=row.is_active,
        last_tested_at=row.last_tested_at,
        last_used_at=row.last_used_at,
        last_error=row.last_error,
        created_at=row.created_at,
    )


@router.get("", response_model=ProviderListOut)
async def list_providers(user: CurrentUser, session: SessionDep) -> ProviderListOut:
    rows = list(
        await session.scalars(
            select(ProviderCredential)
            .where(ProviderCredential.user_id == user.id)
            .order_by(ProviderCredential.created_at)
        )
    )
    return ProviderListOut(
        items=[_serialize(row) for row in rows],
        catalog=public_catalog(),
        fallback_order=list(FALLBACK_ORDER),
        offline_mode=settings.offline_mode,
    )


@router.post("", response_model=ProviderOut, status_code=status.HTTP_201_CREATED)
async def create_provider(
    payload: ProviderIn, user: CurrentUser, session: SessionDep
) -> ProviderOut:
    spec = get_spec(payload.provider)
    if spec is None:
        raise HTTPException(status_code=400, detail="Provedor desconhecido.")
    if await _find(session, user.id, payload.provider) is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Este provedor já está cadastrado. Atualize a credencial existente.",
        )

    key = payload.api_key.strip() if payload.api_key else None
    base_url = payload.base_url or _default_base_url(spec)
    validate_fields(spec, key, base_url)

    row = ProviderCredential(
        user_id=user.id,
        provider=payload.provider,
        api_key_encrypted=encrypt_secret(key) if key else None,
        key_hint=mask_secret(key) if key else None,
        base_url=base_url,
        model=payload.model or spec.default_model,
        is_active=payload.is_active,
    )
    session.add(row)
    await session.commit()
    return _serialize(row)


@router.get("/route", response_model=RouteOut)
async def provider_route(
    user: CurrentUser,
    session: SessionDep,
    task: Annotated[TaskName, Query()] = "chat",
) -> RouteOut:
    """Mostra a cadeia planejada para uma tarefa — sem chave alguma."""
    chain = await resolve_chain(session, user.id, task)
    return RouteOut(
        task=task,
        chain=[
            RouteItem(
                provider=row.provider,
                label=_label(row.provider),
                model=row.model,
            )
            for row in chain
        ],
        offline_mode=settings.offline_mode,
    )


@router.post("/{provider}/test", response_model=ProviderTestOut)
async def test_provider(
    provider: ProviderSlug, user: CurrentUser, session: SessionDep
) -> ProviderTestOut:
    row = await _find(session, user.id, provider)
    if row is None:
        raise HTTPException(status_code=404, detail="Credencial não encontrada.")

    result = await test_connection(row)
    row.last_tested_at = utcnow()
    row.last_error = None if result.ok else result.message
    await session.commit()
    return ProviderTestOut(
        provider=row.provider,
        ok=result.ok,
        status=result.status,
        message=result.message,
        latency_ms=result.latency_ms,
    )


@router.patch("/{provider}", response_model=ProviderOut)
async def update_provider(
    provider: ProviderSlug,
    payload: ProviderUpdateIn,
    user: CurrentUser,
    session: SessionDep,
) -> ProviderOut:
    row = await _find(session, user.id, provider)
    if row is None:
        raise HTTPException(status_code=404, detail="Credencial não encontrada.")
    spec = get_spec(provider)
    if spec is None:
        raise HTTPException(status_code=400, detail="Provedor desconhecido.")

    base_url = payload.base_url or row.base_url
    if payload.api_key is not None:
        key = payload.api_key.strip()
        validate_fields(spec, key, base_url)
        row.api_key_encrypted = encrypt_secret(key) if key else None
        row.key_hint = mask_secret(key) if key else None
    else:
        if spec.needs_key and row.api_key_encrypted is None:
            raise HTTPException(status_code=400, detail="Informe a chave de API.")
        validate_fields(spec, "cadastrada" if spec.needs_key else None, base_url)

    row.base_url = base_url
    if payload.model is not None:
        row.model = payload.model
    if payload.is_active is not None:
        row.is_active = payload.is_active
    row.last_error = None
    await session.commit()
    return _serialize(row)


@router.delete("/{provider}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_provider(provider: ProviderSlug, user: CurrentUser, session: SessionDep) -> None:
    row = await _find(session, user.id, provider)
    if row is None:
        raise HTTPException(status_code=404, detail="Credencial não encontrada.")
    await session.delete(row)
    await session.commit()
