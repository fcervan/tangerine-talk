"""Chamadas OpenAI-compatible e cadeia de fallback do usuário.

A chave é descriptografada apenas no momento da chamada e nunca entra em
resposta, log ou mensagem de erro. Erros são resumidos em códigos estáveis.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from time import perf_counter
from typing import Any

import httpx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..config import settings
from ..models import ProviderCredential
from ..security.keys import SecretUnavailableError, decrypt_secret
from .catalog import TASK_CAPABILITIES, TaskName, get_spec
from .schemas import TestStatus


class ProviderConnectionError(Exception):
    """Credencial ilegível ou provedor inalcançável."""


@dataclass(frozen=True, slots=True)
class TestResult:
    ok: bool
    status: TestStatus
    message: str
    latency_ms: int | None


_ERRORS: dict[int, tuple[TestStatus, str]] = {
    400: ("provider_error", "Requisição recusada pelo provedor."),
    401: ("invalid_key", "Chave recusada pelo provedor."),
    403: ("invalid_key", "Acesso negado pelo provedor."),
    404: ("provider_error", "Modelo não encontrado neste provedor."),
    429: ("quota", "Cota ou limite de requisições esgotado."),
}


def _describe(status_code: int) -> tuple[TestStatus, str]:
    if status_code in _ERRORS:
        return _ERRORS[status_code]
    if status_code >= 500:
        return "provider_error", "Provedor temporariamente indisponível."
    return "provider_error", f"Falha HTTP {status_code}."


def api_key_for(row: ProviderCredential) -> str:
    """Devolve a chave em claro somente para uso interno, nunca para a UI."""
    if not row.api_key_encrypted:
        return ""
    try:
        return decrypt_secret(row.api_key_encrypted)
    except SecretUnavailableError as exc:
        raise ProviderConnectionError(str(exc)) from exc


async def test_connection(row: ProviderCredential) -> TestResult:
    """Faz uma chamada mínima de chat para validar chave, modelo e endpoint."""
    spec = get_spec(row.provider)
    if spec is None:
        return TestResult(False, "provider_error", "Provedor desconhecido.", None)

    try:
        api_key = api_key_for(row)
    except ProviderConnectionError as exc:
        return TestResult(False, "invalid_key", str(exc), None)

    headers = {"Content-Type": "application/json"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
    body: dict[str, Any] = {
        "model": row.model,
        "messages": [{"role": "user", "content": "ping"}],
        "max_tokens": 1,
        "stream": False,
    }
    url = f"{row.base_url.rstrip('/')}/chat/completions"

    started = perf_counter()
    try:
        async with httpx.AsyncClient(timeout=settings.provider_timeout_seconds) as http:
            response = await http.post(url, headers=headers, json=body)
    except httpx.TimeoutException:
        return TestResult(False, "network", "Tempo limite ao contatar o provedor.", None)
    except httpx.RequestError:
        return TestResult(False, "network", "Não foi possível contatar o provedor.", None)

    latency = int((perf_counter() - started) * 1000)
    if 200 <= response.status_code < 300:
        return TestResult(True, "ok", "Conexão OK.", latency)
    status, message = _describe(response.status_code)
    return TestResult(False, status, message, latency)


async def resolve_chain(
    session: AsyncSession, user_id: uuid.UUID, task: TaskName = "chat"
) -> list[ProviderCredential]:
    """Credenciais ativas e capazes, na ordem Groq → Ollama Cloud → OpenRouter.

    `OFFLINE_MODE=1` remove provedores em nuvem da cadeia. O local (Ollama)
    entra por último, inclusive online, como última opção do próprio usuário.
    """
    rows = list(
        await session.scalars(
            select(ProviderCredential).where(
                ProviderCredential.user_id == user_id,
                ProviderCredential.is_active.is_(True),
            )
        )
    )
    needed = TASK_CAPABILITIES.get(task, frozenset({"chat"}))
    ranked: list[tuple[int, str, ProviderCredential]] = []
    for row in rows:
        spec = get_spec(row.provider)
        if spec is None:
            continue
        if settings.offline_mode and spec.cloud:
            continue
        if not needed.issubset(spec.capabilities):
            continue
        ranked.append((spec.fallback_order, str(row.created_at), row))
    ranked.sort(key=lambda item: (item[0], item[1]))
    return [item[2] for item in ranked]
