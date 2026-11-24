"""Esquemas de entrada e saída do domínio de identidade."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Annotated, Literal

from pydantic import AfterValidator, BaseModel, ConfigDict, EmailStr, Field

from ..i18n import normalize_locale

Password = Annotated[str, Field(min_length=12, max_length=128)]
Locale = Annotated[
    str,
    Field(min_length=2, max_length=35),
    AfterValidator(normalize_locale),
]
Level = Literal["A1", "A2", "B1", "B2", "C1", "C2"]
ExerciseMode = Literal["monolingual", "bilingual"]


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    email: EmailStr
    name: str
    role: Literal["owner", "member"]
    ui_language: str
    target_language: str | None = None
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
    target_language: Locale
    level: Level
    daily_goal_minutes: int = Field(default=15, ge=5, le=180)


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
