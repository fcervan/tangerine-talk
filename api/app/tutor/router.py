"""Tutor de IA: chat, correção, TTS e STT (Fase 4).

A chave nunca sai do servidor: a cadeia BYOK é resolvida e chamada aqui.
Em caso de falha de todos os provedores, devolvemos status/aviso para a UI.
"""

from __future__ import annotations

import base64
import json

from fastapi import APIRouter, UploadFile

from ..auth.deps import CurrentUser, SessionDep
from ..i18n import DEFAULT_LOCALE, normalize_locale
from ..models import User
from ..providers.client import (
    chat_with_fallback,
    stt_with_fallback,
    tts_with_fallback,
)
from .schemas import (
    ChatIn,
    ChatOut,
    CorrectionIn,
    CorrectionOut,
    SttIn,
    SttOut,
    TtsIn,
    TtsOut,
)

router = APIRouter(tags=["tutor"])


def _locale(user: User) -> str:
    try:
        return normalize_locale(user.ui_language)
    except ValueError:
        return DEFAULT_LOCALE


@router.post("/tutor/chat", response_model=ChatOut)
async def tutor_chat(payload: ChatIn, user: CurrentUser, session: SessionDep) -> ChatOut:
    messages = [m.model_dump() for m in payload.messages]
    result, tried = await chat_with_fallback(
        session,
        user.id,
        payload.task,
        messages,
        temperature=payload.temperature,
        max_tokens=payload.max_tokens,
    )
    return ChatOut(
        ok=result.ok,
        content=result.content,
        provider=result.provider,
        model=result.model,
        status=result.status,
        message=result.message,
        tried=tried,
    )


@router.post("/tutor/correct", response_model=CorrectionOut)
async def tutor_correct(
    payload: CorrectionIn, user: CurrentUser, session: SessionDep
) -> CorrectionOut:
    ui = payload.ui_language or user.ui_language
    try:
        ui = normalize_locale(ui)
    except ValueError:
        ui = DEFAULT_LOCALE
    target = payload.target_language or user.target_language or ""
    system = (
        "Você é um tutor de idiomas. Compare a resposta do aluno com a resposta "
        "esperada e diga se está correta (aceite variações equivalentes). "
        f"Responda no idioma da interface: {ui}. Idioma estudado: {target}. "
        "Responda APENAS em JSON válido no formato "
        '{"correct": true|false, "feedback": "frase curta"}.'
    )
    user_msg = f"Resposta esperada: {payload.expected}\nResposta do aluno: {payload.answer}\n" + (
        f"Contexto: {payload.context}\n" if payload.context else ""
    )
    messages = [
        {"role": "system", "content": system},
        {"role": "user", "content": user_msg},
    ]
    result, tried = await chat_with_fallback(
        session, user.id, "correction", messages, temperature=0.2, max_tokens=200
    )
    if not result.ok:
        return CorrectionOut(
            ok=False,
            correct=False,
            feedback=result.message,
            provider=result.provider,
            model=result.model,
            status=result.status,
            message=result.message,
            tried=tried,
        )

    correct = False
    feedback = result.content
    try:
        parsed = json.loads(result.content)
        correct = bool(parsed.get("correct"))
        feedback = str(parsed.get("feedback") or result.content)
    except (json.JSONDecodeError, AttributeError, TypeError):
        # modelo não seguiu o formato; tenta inferir
        lowered = result.content.lower()
        correct = "correta" in lowered or "correct" in lowered or "certo" in lowered
    return CorrectionOut(
        ok=True,
        correct=correct,
        feedback=feedback,
        provider=result.provider,
        model=result.model,
        status=result.status,
        message=result.message,
        tried=tried,
    )


@router.post("/tutor/tts", response_model=TtsOut)
async def tutor_tts(payload: TtsIn, user: CurrentUser, session: SessionDep) -> TtsOut:
    result, tried = await tts_with_fallback(
        session, user.id, payload.text, voice=payload.voice, response_format=payload.response_format
    )
    audio_b64 = base64.b64encode(result.audio_base64).decode() if result.audio_base64 else None
    return TtsOut(
        ok=result.ok,
        audio_base64=audio_b64,
        content_type=result.content_type,
        provider=result.provider,
        model=result.model,
        status=result.status,
        message=result.message,
        tried=tried,
    )


@router.post("/tutor/stt", response_model=SttOut)
async def tutor_stt(payload: SttIn, user: CurrentUser, session: SessionDep) -> SttOut:
    try:
        audio_bytes = base64.b64decode(payload.audio_base64)
    except Exception:
        return SttOut(
            ok=False,
            text="",
            provider=None,
            model=None,
            status="provider_error",
            message="Áudio inválido (base64).",
            tried=[],
        )
    result, tried = await stt_with_fallback(
        session, user.id, audio_bytes, content_type=payload.content_type, language=payload.language
    )
    return SttOut(
        ok=result.ok,
        text=result.text,
        provider=result.provider,
        model=result.model,
        status=result.status,
        message=result.message,
        tried=tried,
    )


@router.post("/tutor/stt/upload", response_model=SttOut)
async def tutor_stt_upload(
    file: UploadFile,
    user: CurrentUser,
    session: SessionDep,
    language: str | None = None,
) -> SttOut:
    audio_bytes = await file.read()
    result, tried = await stt_with_fallback(
        session,
        user.id,
        audio_bytes,
        content_type=file.content_type or "audio/webm",
        language=language,
    )
    return SttOut(
        ok=result.ok,
        text=result.text,
        provider=result.provider,
        model=result.model,
        status=result.status,
        message=result.message,
        tried=tried,
    )
