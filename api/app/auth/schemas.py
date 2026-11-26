"""Esquemas de entrada e saída do domínio de identidade."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Annotated, Literal

from pydantic import (
    AfterValidator,
    BaseModel,
    ConfigDict,
    EmailStr,
    Field,
    field_validator,
    model_validator,
)

from ..i18n import normalize_locale

Password = Annotated[str, Field(min_length=12, max_length=128)]
Locale = Annotated[
    str,
    Field(min_length=2, max_length=35),
    AfterValidator(normalize_locale),
]
Level = Literal["A1", "A2", "B1", "B2", "C1", "C2"]
LevelBand = Literal["A1_A2", "B1_B2", "C1_C2", "NONE"]
ProgramSource = Literal["curriculum", "topics"]
ExerciseMode = Literal["monolingual", "bilingual"]
# Provedores que podem ser escolhidos no onboarding (a ordem de fallback é do catálogo).
InferenceProvider = Literal["groq", "ollama_cloud", "openrouter"]


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    email: EmailStr
    name: str
    role: Literal["owner", "member"]
    ui_language: str
    target_language: str | None = None
    study_languages: list[str] = Field(default_factory=list)
    level_band: str | None = None
    program_source: str | None = None
    program_topics: list[str] = Field(default_factory=list)
    inference_provider: str | None = None
    inference_fallbacks: list[str] = Field(default_factory=list)
    onboarding_completed: bool = False
    settings: dict[str, object] = Field(default_factory=dict)
    created_at: datetime


class MemberOut(UserOut):
    last_login_at: datetime | None = None


class LoginIn(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=128)


class RegisterIn(BaseModel):
    token: str = Field(min_length=16, max_length=128)
    name: str = Field(min_length=1, max_length=120)
    password: Password


class RegisterPublicIn(BaseModel):
    email: EmailStr
    name: str = Field(min_length=1, max_length=120)
    password: Password


class InvitePreview(BaseModel):
    email: str
    role: str
    expires_at: datetime


class MeUpdateIn(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=120)
    # Só a interface muda por aqui. O idioma alvo é definido no onboarding.
    ui_language: Locale | None = None
    settings: dict[str, object] | None = None


class OnboardingIn(BaseModel):
    ui_language: Locale
    study_languages: list[Locale] = Field(min_length=1)
    level_band: LevelBand
    program_source: ProgramSource
    program_topics: list[str] = Field(default_factory=list)
    daily_goal_minutes: int = Field(default=15, ge=5, le=180)
    # Servidor de inferência escolhido no onboarding + ordem de fallback.
    inference_provider: InferenceProvider
    inference_fallbacks: list[InferenceProvider] = Field(default_factory=list)
    # Nome do modelo no provedor escolhido. Livre por enquanto; vazio usa o padrão.
    inference_model: str | None = Field(default=None, min_length=1, max_length=120)

    @field_validator("inference_model")
    @classmethod
    def clean_model(cls, value: str | None) -> str | None:
        return value.strip() if value else None

    @field_validator("inference_fallbacks")
    @classmethod
    def clean_fallbacks(cls, value: list[str]) -> list[str]:
        """Sem duplicatas e sem repetir o provedor principal."""
        seen: set[str] = set()
        ordered: list[str] = []
        for item in value:
            if item not in seen:
                seen.add(item)
                ordered.append(item)
        return ordered

    @model_validator(mode="after")
    def check_inference(self) -> "OnboardingIn":
        self.inference_fallbacks = [
            item for item in self.inference_fallbacks if item != self.inference_provider
        ]
        return self


class OnboardingOut(UserOut):
    exercise_mode: ExerciseMode


class PasswordChangeIn(BaseModel):
    current_password: str = Field(min_length=1, max_length=128)
    new_password: Password


class DeleteMeIn(BaseModel):
    password: str = Field(min_length=1, max_length=128)


class InviteIn(BaseModel):
    email: EmailStr


class InviteOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    email: EmailStr
    role: str
    expires_at: datetime
    accepted_at: datetime | None
    created_at: datetime


class InviteCreated(BaseModel):
    invite: InviteOut
    invite_url: str
    email_sent: bool
