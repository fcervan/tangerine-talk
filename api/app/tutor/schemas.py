from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    role: Literal["system", "user", "assistant"]
    content: str = Field(min_length=1, max_length=4000)


class ChatIn(BaseModel):
    messages: list[ChatMessage] = Field(min_length=1, max_length=40)
    task: Literal["chat", "feedback", "correction"] = "chat"
    temperature: float = Field(default=0.4, ge=0.0, le=1.0)
    max_tokens: int = Field(default=400, ge=1, le=2000)


class ChatOut(BaseModel):
    ok: bool
    content: str
    provider: str | None
    model: str | None
    status: str
    message: str
    tried: list[str]


class CorrectionIn(BaseModel):
    target_language: str | None = None
    ui_language: str | None = None
    expected: str = Field(min_length=1, max_length=500)
    answer: str = Field(min_length=1, max_length=500)
    context: str | None = Field(default=None, max_length=500)


class CorrectionOut(BaseModel):
    ok: bool
    correct: bool
    feedback: str
    provider: str | None
    model: str | None
    status: str
    message: str
    tried: list[str]


class TtsIn(BaseModel):
    text: str = Field(min_length=1, max_length=4000)
    voice: str = Field(default="alloy", max_length=50)
    response_format: Literal["mp3", "opus", "aac", "flac"] = "mp3"


class TtsOut(BaseModel):
    ok: bool
    audio_base64: str | None
    content_type: str | None
    provider: str | None
    model: str | None
    status: str
    message: str
    tried: list[str]


class SttIn(BaseModel):
    audio_base64: str = Field(min_length=1)
    content_type: str = Field(default="audio/webm")
    language: str | None = None


class SttOut(BaseModel):
    ok: bool
    text: str
    provider: str | None
    model: str | None
    status: str
    message: str
    tried: list[str]
