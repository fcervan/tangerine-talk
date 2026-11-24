"""Esquemas de gamificação."""

from __future__ import annotations

from datetime import date, datetime
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field


class BadgeSlug(StrEnum):
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
    BRONZE = "bronze"
    SILVER = "silver"
    GOLD = "gold"
    DIAMOND = "diamond"


class MissionType(StrEnum):
    COMPLETE_LESSON = "complete_lesson"
    REVIEW_FLASHCARDS = "review_flashcards"
    PRACTICE_SPEAKING = "practice_speaking"
    PRACTICE_LISTENING = "practice_listening"
    PRACTICE_WRITING = "practice_writing"
    USE_TUTOR = "use_tutor"
    MAINTAIN_STREAK = "maintain_streak"


class BadgeOut(BaseModel):
    slug: BadgeSlug
    earned_at: datetime
    meta: dict[str, Any] = Field(default_factory=dict)


class StreakDayOut(BaseModel):
    day: date
    minutes: int
    lessons_completed: int


class GamificationOut(BaseModel):
    xp: int
    level: int
    current_streak: int
    longest_streak: int
    last_streak_date: date | None
    streak_frozen: bool
    daily_goal_minutes: int
    minutes_today: int
    last_minutes_date: date | None
    league_tier: LeagueTier
    league_xp_this_week: int
    league_rank: int | None
    league_week_start: date | None
    total_lessons_completed: int
    total_conversations: int
    total_flashcards_reviewed: int
    badges: list[BadgeOut] = Field(default_factory=list)


class SRSItemOut(BaseModel):
    item_id: str
    interval_days: int
    ease_factor: float
    repetitions: int
    due_date: date
    last_quality: int | None
    last_reviewed_at: datetime | None


class SRSReviewIn(BaseModel):
    item_id: str
    quality: int = Field(ge=0, le=5)


class SRSReviewOut(BaseModel):
    item_id: str
    interval_days: int
    ease_factor: float
    repetitions: int
    due_date: date
    next_due: date


class MissionOut(BaseModel):
    type: MissionType
    target: int
    progress: int
    completed: bool
    xp_reward: int


class LeagueWeekOut(BaseModel):
    week_start: date
    tier: LeagueTier
    xp: int
    rank: int | None
    promoted: bool
    demoted: bool


class LeaderboardEntry(BaseModel):
    user_id: str
    name: str
    xp: int
    rank: int


class LeaderboardOut(BaseModel):
    week_start: date
    tier: LeagueTier
    entries: list[LeaderboardEntry]
