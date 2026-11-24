"""Esquemas de currículo e baralhos.

A frase avaliada vem sempre no idioma alvo; a glossa, no idioma da interface
(`locale`) com fallback técnico para pt-BR. Nenhum esquema expõe dados de outro
usuário.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

LessonStatus = Literal["locked", "available", "completed"]


class ItemOut(BaseModel):
    id: uuid.UUID
    kind: str
    front_text: str
    example: str | None
    gloss: str
    gloss_locale: str


class ExerciseOut(BaseModel):
    id: uuid.UUID
    type: str
    prompt: str
    answer: str
    options: list[str] | None = None
    order_index: int


class LessonOut(BaseModel):
    id: uuid.UUID
    slug: str
    title: str
    order_index: int
    kind: str
    xp_reward: int
    status: LessonStatus
    exercise_count: int


class LessonDetailOut(LessonOut):
    items: list[ItemOut]
    exercises: list[ExerciseOut]


class UnitOut(BaseModel):
    id: uuid.UUID
    target_language: str
    level: str
    slug: str
    title: str
    description: str | None
    order_index: int
    status: LessonStatus
    lessons: list[LessonOut]


class UnitDetailOut(UnitOut):
    items: list[ItemOut]


class CurriculumLanguagesOut(BaseModel):
    languages: list[str]


class CurriculumOut(BaseModel):
    target_language: str
    level: str | None
    locale: str
    units: list[UnitOut]


class DeckOut(BaseModel):
    id: uuid.UUID
    slug: str
    title: str
    description: str | None
    level: str
    item_count: int
    items: list[ItemOut] = Field(default_factory=list)


class DeckListOut(BaseModel):
    target_language: str
    decks: list[DeckOut]


class CompleteIn(BaseModel):
    score: int | None = Field(default=None, ge=0, le=100)


class CompleteOut(BaseModel):
    lesson_id: uuid.UUID
    status: Literal["completed", "already_completed"]
    xp_earned: int
    completed_at: datetime
