"""Modelos registrados na metadata (importados pelo Alembic)."""

from .content import (
    ContentOutbox,
    Deck,
    DeckItem,
    Exercise,
    Item,
    ItemTranslation,
    Lesson,
    OutboxEventType,
    Unit,
    UserLessonProgress,
)
from .gamification import (
    UserBadge,
    UserGamification,
    UserLeagueWeek,
    UserMission,
    UserSRSItem,
    UserStreakDay,
)
from .provider import ProviderCredential
from .user import AuthSession, Invite, User

__all__ = [
    "AuthSession",
    "ContentOutbox",
    "Deck",
    "DeckItem",
    "Exercise",
    "Invite",
    "Item",
    "ItemTranslation",
    "Lesson",
    "OutboxEventType",
    "ProviderCredential",
    "Unit",
    "User",
    "UserBadge",
    "UserGamification",
    "UserLeagueWeek",
    "UserLessonProgress",
    "UserMission",
    "UserSRSItem",
    "UserStreakDay",
]
