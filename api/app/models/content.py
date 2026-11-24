"""Modelos de conteúdo: trilha, lições, itens, exercícios e baralhos oficiais.

MySQL é a fonte da verdade. Qdrant, quando entrar, será índice derivado —
nunca o lugar onde o currículo de fato vive.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from enum import StrEnum
from typing import Any

from sqlalchemy import (
    JSON,
    Boolean,
    CheckConstraint,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
)
from sqlalchemy import (
    Enum as SAEnum,
)
from sqlalchemy.orm import Mapped, mapped_column

from ..db import Base
from .base import Timestamp, UUIDBinary, utcnow, uuid7

LEVELS = ("A1", "A2", "B1", "B2", "C1", "C2")
EXERCISE_TYPES = ("flashcard", "multiple_choice", "translation")


class Unit(Base):
    """Nó da trilha. Pré-requisito forma a árvore; `order_index` ordena irmãos."""

    __tablename__ = "units"
    __table_args__ = (
        CheckConstraint("level IN ('A1','A2','B1','B2','C1','C2')", name="ck_units_level"),
        UniqueConstraint("target_language", "slug", name="uq_units_target_slug"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUIDBinary, primary_key=True, default=uuid7)
    target_language: Mapped[str] = mapped_column(String(35), index=True)
    level: Mapped[str] = mapped_column(String(2))
    slug: Mapped[str] = mapped_column(String(80))
    title: Mapped[str] = mapped_column(String(160))
    description: Mapped[str | None] = mapped_column(String(500), nullable=True)
    order_index: Mapped[int] = mapped_column(Integer, default=0)
    prerequisite_id: Mapped[uuid.UUID | None] = mapped_column(
        UUIDBinary, ForeignKey("units.id", ondelete="SET NULL"), nullable=True
    )
    is_published: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(Timestamp, default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(Timestamp, default=utcnow, onupdate=utcnow)


class Lesson(Base):
    __tablename__ = "lessons"
    __table_args__ = (
        CheckConstraint("kind IN ('lesson','review')", name="ck_lessons_kind"),
        UniqueConstraint("unit_id", "slug", name="uq_lessons_unit_slug"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUIDBinary, primary_key=True, default=uuid7)
    unit_id: Mapped[uuid.UUID] = mapped_column(
        UUIDBinary, ForeignKey("units.id", ondelete="CASCADE"), index=True
    )
    slug: Mapped[str] = mapped_column(String(80))
    title: Mapped[str] = mapped_column(String(160))
    order_index: Mapped[int] = mapped_column(Integer, default=0)
    kind: Mapped[str] = mapped_column(String(16), default="lesson")
    xp_reward: Mapped[int] = mapped_column(Integer, default=10)
    is_published: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(Timestamp, default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(Timestamp, default=utcnow, onupdate=utcnow)


class Item(Base):
    """Palavra ou frase no idioma estudado. Glossas ficam em `item_translations`."""

    __tablename__ = "items"
    __table_args__ = (CheckConstraint("kind IN ('word','phrase')", name="ck_items_kind"),)

    id: Mapped[uuid.UUID] = mapped_column(UUIDBinary, primary_key=True, default=uuid7)
    lesson_id: Mapped[uuid.UUID] = mapped_column(
        UUIDBinary, ForeignKey("lessons.id", ondelete="CASCADE"), index=True
    )
    kind: Mapped[str] = mapped_column(String(16), default="word")
    front_text: Mapped[str] = mapped_column(String(255))
    example: Mapped[str | None] = mapped_column(String(500), nullable=True)
    order_index: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(Timestamp, default=utcnow)


class ItemTranslation(Base):
    """Glossa por locale da interface. Fallback técnico é sempre `pt-BR`."""

    __tablename__ = "item_translations"

    item_id: Mapped[uuid.UUID] = mapped_column(
        UUIDBinary, ForeignKey("items.id", ondelete="CASCADE"), primary_key=True
    )
    locale: Mapped[str] = mapped_column(String(35), primary_key=True)
    gloss: Mapped[str] = mapped_column(String(500))


class Exercise(Base):
    """Exercício pronto para o player da Fase 4. Sem áudio ainda."""

    __tablename__ = "exercises"
    __table_args__ = (
        CheckConstraint(
            "type IN ('flashcard','multiple_choice','translation')",
            name="ck_exercises_type",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUIDBinary, primary_key=True, default=uuid7)
    lesson_id: Mapped[uuid.UUID] = mapped_column(
        UUIDBinary, ForeignKey("lessons.id", ondelete="CASCADE"), index=True
    )
    item_id: Mapped[uuid.UUID | None] = mapped_column(
        UUIDBinary, ForeignKey("items.id", ondelete="SET NULL"), nullable=True
    )
    type: Mapped[str] = mapped_column(String(24))
    prompt: Mapped[str] = mapped_column(String(500))
    answer: Mapped[str] = mapped_column(String(500))
    options: Mapped[list[str] | None] = mapped_column(JSON, nullable=True)
    order_index: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(Timestamp, default=utcnow)


class Deck(Base):
    """Baralho: oficiais (currículo) ou próprios do usuário.

    - Oficiais: `is_official=True`, `user_id=NULL`, únicos por `target_language` + `slug`
    - Próprios: `is_official=False`, `user_id` preenchido, únicos por `user_id` + `slug`
    """

    __tablename__ = "decks"
    __table_args__ = (
        CheckConstraint("level IN ('A1','A2','B1','B2','C1','C2')", name="ck_decks_level"),
        UniqueConstraint("target_language", "slug", name="uq_decks_target_slug"),
        UniqueConstraint("user_id", "slug", name="uq_decks_user_slug"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUIDBinary, primary_key=True, default=uuid7)
    target_language: Mapped[str] = mapped_column(String(35), index=True)
    level: Mapped[str] = mapped_column(String(2))
    slug: Mapped[str] = mapped_column(String(80))
    title: Mapped[str] = mapped_column(String(160))
    description: Mapped[str | None] = mapped_column(String(500), nullable=True)
    is_official: Mapped[bool] = mapped_column(Boolean, default=True)
    user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUIDBinary, ForeignKey("users.id", ondelete="CASCADE"), nullable=True, index=True
    )
    created_at: Mapped[datetime] = mapped_column(Timestamp, default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(Timestamp, default=utcnow, onupdate=utcnow)


class DeckItem(Base):
    __tablename__ = "deck_items"

    deck_id: Mapped[uuid.UUID] = mapped_column(
        UUIDBinary, ForeignKey("decks.id", ondelete="CASCADE"), primary_key=True
    )
    item_id: Mapped[uuid.UUID] = mapped_column(
        UUIDBinary, ForeignKey("items.id", ondelete="CASCADE"), primary_key=True
    )


class UserLessonProgress(Base):
    """Conclusão mínima por lição — alimenta o status da trilha."""

    __tablename__ = "user_lesson_progress"
    __table_args__ = (UniqueConstraint("user_id", "lesson_id", name="uq_progress_user_lesson"),)

    id: Mapped[uuid.UUID] = mapped_column(UUIDBinary, primary_key=True, default=uuid7)
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUIDBinary, ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    lesson_id: Mapped[uuid.UUID] = mapped_column(
        UUIDBinary, ForeignKey("lessons.id", ondelete="CASCADE"), index=True
    )
    completed_at: Mapped[datetime] = mapped_column(Timestamp, default=utcnow)
    score: Mapped[int | None] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(Timestamp, default=utcnow)


class OutboxEventType(StrEnum):
    ITEM_UPSERT = "item_upsert"
    ITEM_DELETE = "item_delete"
    DECK_UPSERT = "deck_upsert"
    DECK_DELETE = "deck_delete"


class ContentOutbox(Base):
    """Outbox para sincronização MySQL → Qdrant.

    Eventos são inseridos na mesma transação que altera o conteúdo.
    Um worker periódico lê e aplica no Qdrant.
    """

    __tablename__ = "content_outbox"
    __table_args__ = (
        {"mysql_charset": "utf8mb4", "mysql_collate": "utf8mb4_0900_as_cs"},
    )

    id: Mapped[uuid.UUID] = mapped_column(UUIDBinary, primary_key=True, default=uuid7)
    event_type: Mapped[str] = mapped_column(SAEnum(OutboxEventType), nullable=False, index=True)
    entity_id: Mapped[uuid.UUID] = mapped_column(UUIDBinary, nullable=False, index=True)
    target_language: Mapped[str] = mapped_column(String(35), nullable=False, index=True)
    payload: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(Timestamp, default=utcnow)
    processed_at: Mapped[datetime | None] = mapped_column(Timestamp, nullable=True, index=True)
    attempts: Mapped[int] = mapped_column(default=0)
    last_error: Mapped[str | None] = mapped_column(String(500), nullable=True)
