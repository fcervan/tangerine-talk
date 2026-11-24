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
from ..models.base import utcnow
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


@dataclass(frozen=True, slots=True)
class ChatResult:
    ok: bool
    status: TestStatus
    content: str
    provider: str | None
    model: str | None
    latency_ms: int | None
    message: str


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


async def chat_completion(
    row: ProviderCredential,
    messages: list[dict[str, str]],
    *,
    temperature: float = 0.4,
    max_tokens: int = 400,
) -> ChatResult:
    """Chamada de chat usando a credencial indicada. Não tenta fallback."""
    spec = get_spec(row.provider)
    if spec is None:
        return ChatResult(
            False, "provider_error", "", row.provider, row.model, None, "Provedor desconhecido."
        )

    try:
        api_key = api_key_for(row)
    except ProviderConnectionError as exc:
        return ChatResult(False, "invalid_key", "", row.provider, row.model, None, str(exc))

    headers = {"Content-Type": "application/json"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
    body: dict[str, Any] = {
        "model": row.model,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
        "stream": False,
    }
    url = f"{row.base_url.rstrip('/')}/chat/completions"
    started = perf_counter()
    try:
        async with httpx.AsyncClient(timeout=settings.provider_timeout_seconds) as http:
            response = await http.post(url, headers=headers, json=body)
    except httpx.TimeoutException:
        return ChatResult(
            False,
            "network",
            "",
            row.provider,
            row.model,
            None,
            "Tempo limite ao contatar o provedor.",
        )
    except httpx.RequestError:
        return ChatResult(
            False,
            "network",
            "",
            row.provider,
            row.model,
            None,
            "Não foi possível contatar o provedor.",
        )

    latency = int((perf_counter() - started) * 1000)
    if not (200 <= response.status_code < 300):
        status, message = _describe(response.status_code)
        return ChatResult(False, status, "", row.provider, row.model, latency, message)

    try:
        data = response.json()
        content = (data.get("choices") or [{}])[0].get("message", {}).get("content", "")
        content = (content or "").strip()
    except (ValueError, AttributeError, IndexError):
        return ChatResult(
            False,
            "provider_error",
            "",
            row.provider,
            row.model,
            latency,
            "Resposta inválida do provedor.",
        )
    if not content:
        return ChatResult(
            False,
            "provider_error",
            "",
            row.provider,
            row.model,
            latency,
            "Resposta vazia do provedor.",
        )
    return ChatResult(True, "ok", content, row.provider, row.model, latency, "OK")


async def chat_with_fallback(
    session: AsyncSession,
    user_id: uuid.UUID,
    task: TaskName,
    messages: list[dict[str, str]],
    *,
    temperature: float = 0.4,
    max_tokens: int = 400,
) -> tuple[ChatResult, list[str]]:
    """Tenta a cadeia do usuário; devolve o resultado e a lista de provedores tentados."""
    chain = await resolve_chain(session, user_id, task)
    if not chain:
        return ChatResult(
            False,
            "provider_error",
            "",
            None,
            None,
            None,
            "Nenhum provedor configurado para esta tarefa.",
        ), []

    tried: list[str] = []
    last: ChatResult | None = None
    for row in chain:
        tried.append(row.provider)
        result = await chat_completion(
            row, messages, temperature=temperature, max_tokens=max_tokens
        )
        if result.ok:
            row.last_used_at = utcnow()
            await session.commit()
            return result, tried
        last = result
        # quota/invalid_key: tenta o próximo; network/provider_error também.
    assert last is not None
    return last, tried


@dataclass(frozen=True, slots=True)
class TtsResult:
    ok: bool
    status: TestStatus
    audio_base64: bytes | None
    content_type: str | None
    provider: str | None
    model: str | None
    latency_ms: int | None
    message: str


@dataclass(frozen=True, slots=True)
class SttResult:
    ok: bool
    status: TestStatus
    text: str
    provider: str | None
    model: str | None
    latency_ms: int | None
    message: str


async def tts_synthesize(
    row: ProviderCredential,
    text: str,
    *,
    voice: str = "alloy",
    response_format: str = "mp3",
) -> TtsResult:
    """Síntese de fala via provedor (OpenAI-compatible /audio/speech)."""
    spec = get_spec(row.provider)
    if spec is None or "tts" not in spec.capabilities:
        return TtsResult(
            ok=False,
            status="provider_error",
            audio_base64=None,
            content_type=None,
            provider=row.provider,
            model=row.model,
            latency_ms=None,
            message="Provedor não suporta TTS.",
        )

    try:
        api_key = api_key_for(row)
    except ProviderConnectionError as exc:
        return TtsResult(
            ok=False,
            status="invalid_key",
            audio_base64=None,
            content_type=None,
            provider=row.provider,
            model=row.model,
            latency_ms=None,
            message=str(exc),
        )

    headers = {"Content-Type": "application/json"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
    body: dict[str, Any] = {
        "model": row.model,
        "input": text,
        "voice": voice,
        "response_format": response_format,
    }
    url = f"{row.base_url.rstrip('/')}/audio/speech"
    started = perf_counter()
    try:
        async with httpx.AsyncClient(timeout=settings.provider_timeout_seconds) as http:
            response = await http.post(url, headers=headers, json=body)
    except httpx.TimeoutException:
        return TtsResult(
            ok=False,
            status="network",
            audio_base64=None,
            content_type=None,
            provider=row.provider,
            model=row.model,
            latency_ms=None,
            message="Tempo limite ao contatar o provedor.",
        )
    except httpx.RequestError:
        return TtsResult(
            ok=False,
            status="network",
            audio_base64=None,
            content_type=None,
            provider=row.provider,
            model=row.model,
            latency_ms=None,
            message="Não foi possível contatar o provedor.",
        )

    latency = int((perf_counter() - started) * 1000)
    if not (200 <= response.status_code < 300):
        status, message = _describe(response.status_code)
        return TtsResult(
            ok=False,
            status=status,
            audio_base64=None,
            content_type=None,
            provider=row.provider,
            model=row.model,
            latency_ms=latency,
            message=message,
        )

    content_type = response.headers.get("content-type", "audio/mpeg")
    audio_b64 = response.content
    return TtsResult(
        ok=True,
        status="ok",
        audio_base64=audio_b64,
        content_type=content_type,
        provider=row.provider,
        model=row.model,
        latency_ms=latency,
        message="OK",
    )


async def stt_transcribe(
    row: ProviderCredential,
    audio_bytes: bytes,
    *,
    file_name: str = "audio.webm",
    content_type: str = "audio/webm",
    language: str | None = None,
) -> SttResult:
    """Transcrição de áudio via provedor (OpenAI-compatible /audio/transcriptions)."""
    spec = get_spec(row.provider)
    if spec is None or "stt" not in spec.capabilities:
        return SttResult(
            ok=False,
            status="provider_error",
            text="",
            provider=row.provider,
            model=row.model,
            latency_ms=None,
            message="Provedor não suporta STT.",
        )

    try:
        api_key = api_key_for(row)
    except ProviderConnectionError as exc:
        return SttResult(
            ok=False,
            status="invalid_key",
            text="",
            provider=row.provider,
            model=row.model,
            latency_ms=None,
            message=str(exc),
        )

    headers = {}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
    files = {"file": (file_name, audio_bytes, content_type)}
    data = {"model": row.model}
    if language:
        data["language"] = language
    url = f"{row.base_url.rstrip('/')}/audio/transcriptions"
    started = perf_counter()
    try:
        async with httpx.AsyncClient(timeout=settings.provider_timeout_seconds) as http:
            response = await http.post(url, headers=headers, files=files, data=data)
    except httpx.TimeoutException:
        return SttResult(
            ok=False,
            status="network",
            text="",
            provider=row.provider,
            model=row.model,
            latency_ms=None,
            message="Tempo limite ao contatar o provedor.",
        )
    except httpx.RequestError:
        return SttResult(
            ok=False,
            status="network",
            text="",
            provider=row.provider,
            model=row.model,
            latency_ms=None,
            message="Não foi possível contatar o provedor.",
        )

    latency = int((perf_counter() - started) * 1000)
    if not (200 <= response.status_code < 300):
        status, message = _describe(response.status_code)
        return SttResult(
            ok=False,
            status=status,
            text="",
            provider=row.provider,
            model=row.model,
            latency_ms=latency,
            message=message,
        )

    try:
        data = response.json()
        text = (data.get("text") or "").strip()
    except (ValueError, AttributeError):
        return SttResult(
            ok=False,
            status="provider_error",
            text="",
            provider=row.provider,
            model=row.model,
            latency_ms=latency,
            message="Resposta inválida do provedor.",
        )
    return SttResult(
        ok=True,
        status="ok",
        text=text,
        provider=row.provider,
        model=row.model,
        latency_ms=latency,
        message="OK",
    )


async def tts_with_fallback(
    session: AsyncSession,
    user_id: uuid.UUID,
    text: str,
    *,
    voice: str = "alloy",
    response_format: str = "mp3",
) -> tuple[TtsResult, list[str]]:
    chain = await resolve_chain(session, user_id, "tts")
    if not chain:
        return (
            TtsResult(
                ok=False,
                status="provider_error",
                audio_base64=None,
                content_type=None,
                provider=None,
                model=None,
                latency_ms=None,
                message="Nenhum provedor configurado para TTS.",
            ),
            [],
        )

    tried: list[str] = []
    last: TtsResult | None = None
    for row in chain:
        tried.append(row.provider)
        result = await tts_synthesize(row, text, voice=voice, response_format=response_format)
        if result.ok:
            row.last_used_at = utcnow()
            await session.commit()
            return result, tried
        last = result
    assert last is not None
    return last, tried


async def stt_with_fallback(
    session: AsyncSession,
    user_id: uuid.UUID,
    audio_bytes: bytes,
    *,
    file_name: str = "audio.webm",
    content_type: str = "audio/webm",
    language: str | None = None,
) -> tuple[SttResult, list[str]]:
    chain = await resolve_chain(session, user_id, "stt")
    if not chain:
        return (
            SttResult(
                ok=False,
                status="provider_error",
                text="",
                provider=None,
                model=None,
                latency_ms=None,
                message="Nenhum provedor configurado para STT.",
            ),
            [],
        )

    tried: list[str] = []
    last: SttResult | None = None
    for row in chain:
        tried.append(row.provider)
        result = await stt_transcribe(
            row, audio_bytes, file_name=file_name, content_type=content_type, language=language
        )
        if result.ok:
            row.last_used_at = utcnow()
            await session.commit()
            return result, tried
        last = result
    assert last is not None
    return last, tried
