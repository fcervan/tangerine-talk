"""Modelos de gamificação: XP, streak, SRS, selos, ligas e missões.

Tudo persistido no MySQL. Sem billing, sem paywall.
"""

from __future__ import annotations

import uuid
from datetime import date, datetime
from enum import StrEnum
from typing import Any

from sqlalchemy import (
    JSON,
    Boolean,
    Date,
    ForeignKey,
    Index,
    Integer,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column

from ..db import Base
from .base import Timestamp, UUIDBinary, utcnow, uuid7


class BadgeSlug(StrEnum):
    """Selos disponíveis — expansíveis sem migração de schema."""

    STREAK_7 = "streak_7"
    STREAK_30 = "streak_30"
    STREAK_100 = "streak_100"
    CONV_1 = "conversations_1"
    CONV_25 = "conversations_25"
    CONV_50 = "conversations_50"
    FIRST_LESSON = "first_lesson"
    FIRST_DECK = "first_deck"
    WEEK_LEAGUE_WIN = "week_league_win"


class LeagueTier(StrEnum):
    """Patamares da liga semanal (promoção/rebaixamento)."""

    BRONZE = "bronze"
    SILVER = "silver"
    GOLD = "gold"
    DIAMOND = "diamond"


class MissionType(StrEnum):
    """Tipos de missão diária."""

    COMPLETE_LESSON = "complete_lesson"
    REVIEW_FLASHCARDS = "review_flashcards"
    PRACTICE_SPEAKING = "practice_speaking"
    PRACTICE_LISTENING = "practice_listening"
    PRACTICE_WRITING = "practice_writing"
    USE_TUTOR = "use_tutor"
    MAINTAIN_STREAK = "maintain_streak"


class UserGamification(Base):
    """Resumo agregado de progresso do usuário — lido com frequência."""

    __tablename__ = "user_gamification"
    __table_args__ = (
        UniqueConstraint("user_id", name="uq_gamification_user"),
        Index("ix_gamification_xp", "xp"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUIDBinary, primary_key=True, default=uuid7)
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUIDBinary, ForeignKey("users.id", ondelete="CASCADE"), unique=True, index=True
    )
    # XP total
    xp: Mapped[int] = mapped_column(Integer, default=0)
    # Nível calculado a partir do XP (ex.: 100 XP por nível)
    level: Mapped[int] = mapped_column(Integer, default=1)
    # Streak
    current_streak: Mapped[int] = mapped_column(Integer, default=0)
    longest_streak: Mapped[int] = mapped_column(Integer, default=0)
    last_streak_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    streak_frozen: Mapped[bool] = mapped_column(Boolean, default=False)
    # Meta diária (minutos)
    daily_goal_minutes: Mapped[int] = mapped_column(Integer, default=15)
    minutes_today: Mapped[int] = mapped_column(Integer, default=0)
    last_minutes_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    # Liga semanal
    league_tier: Mapped[str] = mapped_column(String(16), default=LeagueTier.BRONZE.value)
    league_xp_this_week: Mapped[int] = mapped_column(Integer, default=0)
    league_rank: Mapped[int | None] = mapped_column(Integer, nullable=True)
    league_week_start: Mapped[date | None] = mapped_column(Date, nullable=True)
    # Totais para selos
    total_lessons_completed: Mapped[int] = mapped_column(Integer, default=0)
    total_conversations: Mapped[int] = mapped_column(Integer, default=0)
    total_flashcards_reviewed: Mapped[int] = mapped_column(Integer, default=0)
    # Metadados
    created_at: Mapped[datetime] = mapped_column(Timestamp, default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(Timestamp, default=utcnow, onupdate=utcnow)


class UserStreakDay(Base):
    """Registro diário de streak — um por dia em que o usuário praticou."""

    __tablename__ = "user_streak_days"
    __table_args__ = (
        UniqueConstraint("user_id", "day", name="uq_streak_user_day"),
        Index("ix_streak_user_day", "user_id", "day"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUIDBinary, primary_key=True, default=uuid7)
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUIDBinary, ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    day: Mapped[date] = mapped_column(Date)
    minutes: Mapped[int] = mapped_column(Integer, default=0)
    lessons_completed: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(Timestamp, default=utcnow)


class UserBadge(Base):
    """Selo conquistado pelo usuário."""

    __tablename__ = "user_badges"
    __table_args__ = (
        UniqueConstraint("user_id", "slug", name="uq_badge_user_slug"),
        Index("ix_badge_user_slug", "user_id", "slug"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUIDBinary, primary_key=True, default=uuid7)
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUIDBinary, ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    slug: Mapped[str] = mapped_column(String(64))  # BadgeSlug
    earned_at: Mapped[datetime] = mapped_column(Timestamp, default=utcnow)
    # Metadados extras (ex.: streak no momento, liga)
    meta: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)


class UserSRSItem(Base):
    """Item de repetição espaçada (SM-2 simplificado).

    - interval_days: intervalo atual em dias
    - ease_factor: fator de facilidade (2.5 inicial)
    - due_date: quando o item vence para revisão
    """

    __tablename__ = "user_srs_items"
    __table_args__ = (
        UniqueConstraint("user_id", "item_id", name="uq_srs_user_item"),
        Index("ix_srs_user_due", "user_id", "due_date"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUIDBinary, primary_key=True, default=uuid7)
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUIDBinary, ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    item_id: Mapped[uuid.UUID] = mapped_column(
        UUIDBinary, ForeignKey("items.id", ondelete="CASCADE"), index=True
    )
    # Estado SM-2
    interval_days: Mapped[int] = mapped_column(Integer, default=0)
    ease_factor: Mapped[float] = mapped_column(default=2.5)
    repetitions: Mapped[int] = mapped_column(Integer, default=0)
    due_date: Mapped[date] = mapped_column(Date, index=True)
    # Qualidade da última resposta (0-5, para algoritmo)
    last_quality: Mapped[int | None] = mapped_column(Integer, nullable=True)
    last_reviewed_at: Mapped[datetime | None] = mapped_column(Timestamp, nullable=True)
    created_at: Mapped[datetime] = mapped_column(Timestamp, default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(Timestamp, default=utcnow, onupdate=utcnow)


class UserLeagueWeek(Base):
    """Snapshot semanal da liga — congelado no fim da semana para histórico."""

    __tablename__ = "user_league_weeks"
    __table_args__ = (
        UniqueConstraint("user_id", "week_start", name="uq_league_user_week"),
        Index("ix_league_week_tier_rank", "week_start", "tier", "rank"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUIDBinary, primary_key=True, default=uuid7)
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUIDBinary, ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    week_start: Mapped[date] = mapped_column(Date)
    tier: Mapped[str] = mapped_column(String(16))  # LeagueTier
    xp: Mapped[int] = mapped_column(Integer, default=0)
    rank: Mapped[int | None] = mapped_column(Integer, nullable=True)
    promoted: Mapped[bool] = mapped_column(Boolean, default=False)
    demoted: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(Timestamp, default=utcnow)


class UserMission(Base):
    """Missão diária ativa/completa."""

    __tablename__ = "user_missions"
    __table_args__ = (
        UniqueConstraint("user_id", "day", "type", name="uq_mission_user_day_type"),
        Index("ix_mission_user_day", "user_id", "day"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUIDBinary, primary_key=True, default=uuid7)
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUIDBinary, ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    day: Mapped[date] = mapped_column(Date)
    type: Mapped[str] = mapped_column(String(32))  # MissionType
    target: Mapped[int] = mapped_column(Integer, default=1)
    progress: Mapped[int] = mapped_column(Integer, default=0)
    completed: Mapped[bool] = mapped_column(Boolean, default=False)
    xp_reward: Mapped[int] = mapped_column(Integer, default=5)
    created_at: Mapped[datetime] = mapped_column(Timestamp, default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(Timestamp, default=utcnow, onupdate=utcnow)
