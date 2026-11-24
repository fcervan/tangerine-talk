"""Modelos registrados na metadata (importados pelo Alembic)."""

from .content import (
    Deck,
    DeckItem,
    Exercise,
    Item,
    ItemTranslation,
    Lesson,
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
    "Deck",
    "DeckItem",
    "Exercise",
    "Invite",
    "Item",
    "ItemTranslation",
    "Lesson",
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
