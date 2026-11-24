"""Lógica de gamificação: XP, streak, SRS, selos, ligas, missões."""

from __future__ import annotations

import random
import uuid
from collections.abc import Sequence
from datetime import UTC, date, datetime, timedelta

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models import (
    UserBadge,
    UserGamification,
    UserLeagueWeek,
    UserMission,
    UserSRSItem,
    UserStreakDay,
)
from ..models.base import utcnow, uuid7
from .schemas import MissionType

XP_PER_LEVEL = 100
STREAK_BADGES = {7: "streak_7", 30: "streak_30", 100: "streak_100"}
CONV_BADGES = {1: "conversations_1", 25: "conversations_25", 50: "conversations_50"}
FIRST_BADGES = ["first_lesson", "first_deck", "week_league_win"]


def _today() -> date:
    return datetime.now(UTC).date()


def _week_start(d: date) -> date:
    return d - timedelta(days=d.weekday())


def _level_from_xp(xp: int) -> int:
    return max(1, xp // XP_PER_LEVEL + 1)


async def get_or_create_gamification(session: AsyncSession, user_id: uuid.UUID) -> UserGamification:
    """Busca ou cria o registro de gamificação do usuário."""
    result = await session.scalar(
        select(UserGamification).where(UserGamification.user_id == user_id)
    )
    if result is not None:
        return result
    g = UserGamification(id=uuid7(), user_id=user_id)
    session.add(g)
    await session.flush()
    return g


async def ensure_streak_day(
    session: AsyncSession, user_id: uuid.UUID, minutes: int = 0, lessons: int = 0
) -> UserStreakDay:
    """Garante registro de streak para hoje."""
    today = _today()
    existing = await session.scalar(
        select(UserStreakDay).where(UserStreakDay.user_id == user_id, UserStreakDay.day == today)
    )
    if existing:
        existing.minutes += minutes
        existing.lessons_completed += lessons
        return existing
    sd = UserStreakDay(
        id=uuid7(), user_id=user_id, day=today, minutes=minutes, lessons_completed=lessons
    )
    session.add(sd)
    return sd


async def update_streak(session: AsyncSession, gam: UserGamification) -> bool:
    """Atualiza streak baseado no último dia de prática. Retorna True se streak aumentou."""
    today = _today()
    if gam.last_streak_date == today:
        return False

    if gam.last_streak_date is None:
        # primeiro dia
        gam.current_streak = 1
        gam.longest_streak = max(gam.longest_streak, 1)
        gam.last_streak_date = today
        return True

    yesterday = today - timedelta(days=1)
    if gam.last_streak_date == yesterday:
        # continua streak
        gam.current_streak += 1
        gam.longest_streak = max(gam.longest_streak, gam.current_streak)
        gam.last_streak_date = today
        return True

    if gam.last_streak_date < yesterday:
        # streak quebrado
        gam.current_streak = 1
        gam.last_streak_date = today
        return True

    return False


async def check_streak_badges(session: AsyncSession, gam: UserGamification) -> list[UserBadge]:
    """Verifica e concede selos de streak."""
    new_badges: list[UserBadge] = []
    for days, slug in STREAK_BADGES.items():
        if gam.current_streak >= days:
            existing = await session.scalar(
                select(UserBadge).where(UserBadge.user_id == gam.user_id, UserBadge.slug == slug)
            )
            if not existing:
                badge = UserBadge(
                    id=uuid7(),
                    user_id=gam.user_id,
                    slug=slug,
                    meta={"streak_at_earned": gam.current_streak},
                )
                session.add(badge)
                new_badges.append(badge)
    return new_badges


async def check_conversation_badges(
    session: AsyncSession, gam: UserGamification
) -> list[UserBadge]:
    """Verifica e concede selos de conversas."""
    new_badges: list[UserBadge] = []
    for count, slug in CONV_BADGES.items():
        if gam.total_conversations >= count:
            existing = await session.scalar(
                select(UserBadge).where(UserBadge.user_id == gam.user_id, UserBadge.slug == slug)
            )
            if not existing:
                badge = UserBadge(
                    id=uuid7(),
                    user_id=gam.user_id,
                    slug=slug,
                    meta={"conversations_at_earned": gam.total_conversations},
                )
                session.add(badge)
                new_badges.append(badge)
    return new_badges


async def check_first_badges(
    session: AsyncSession, gam: UserGamification, badge_slug: str
) -> list[UserBadge]:
    """Verifica selos únicos (first_lesson, first_deck, week_league_win)."""
    if badge_slug not in FIRST_BADGES:
        return []
    existing = await session.scalar(
        select(UserBadge).where(UserBadge.user_id == gam.user_id, UserBadge.slug == badge_slug)
    )
    if not existing:
        badge = UserBadge(id=uuid7(), user_id=gam.user_id, slug=badge_slug, meta={})
        session.add(badge)
        return [badge]
    return []


def sm2_next(
    ease_factor: float, interval_days: int, repetitions: int, quality: int
) -> tuple[float, int, int, date]:
    """Algoritmo SM-2 simplificado. Quality: 0-5 (5 = perfeito)."""
    if quality < 3:
        # Falhou: reseta
        return 2.5, 0, 0, _today()

    if repetitions == 0:
        new_interval = 1
    elif repetitions == 1:
        new_interval = 6
    else:
        new_interval = round(interval_days * ease_factor)

    # Ajusta ease factor
    new_ef = ease_factor + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02))
    new_ef = max(1.3, new_ef)

    next_due = _today() + timedelta(days=new_interval)
    return new_ef, new_interval, repetitions + 1, next_due


async def update_srs(
    session: AsyncSession,
    user_id: uuid.UUID,
    item_id: uuid.UUID,
    quality: int,  # 0-5
) -> UserSRSItem:
    """Atualiza item SRS após revisão."""
    result = await session.scalar(
        select(UserSRSItem).where(UserSRSItem.user_id == user_id, UserSRSItem.item_id == item_id)
    )
    _today()
    if result is None:
        ef, interval, reps, due = sm2_next(2.5, 0, 0, quality)
        srs = UserSRSItem(
            id=uuid7(),
            user_id=user_id,
            item_id=item_id,
            interval_days=interval,
            ease_factor=ef,
            repetitions=reps,
            due_date=due,
            last_quality=quality,
            last_reviewed_at=utcnow(),
        )
        session.add(srs)
        return srs

    ef, interval, reps, due = sm2_next(
        result.ease_factor, result.interval_days, result.repetitions, quality
    )
    result.ease_factor = ef
    result.interval_days = interval
    result.repetitions = reps
    result.due_date = due
    result.last_quality = quality
    result.last_reviewed_at = utcnow()
    return result


async def get_due_srs(
    session: AsyncSession, user_id: uuid.UUID, limit: int = 50
) -> Sequence[UserSRSItem]:
    """Busca itens vencidos para revisão."""
    today = _today()
    result = await session.scalars(
        select(UserSRSItem)
        .where(UserSRSItem.user_id == user_id, UserSRSItem.due_date <= today)
        .order_by(UserSRSItem.due_date)
        .limit(limit)
    )
    return list(result)


async def add_xp(
    session: AsyncSession, gam: UserGamification, xp: int
) -> tuple[int, int, list[UserBadge]]:
    """Adiciona XP e retorna (novo_xp, novo_level, novos_selos)."""
    gam.xp += xp
    gam.level = _level_from_xp(gam.xp)
    new_badges: list[UserBadge] = []
    # Selos de nível podem ser adicionados aqui no futuro
    return gam.xp, gam.level, new_badges


async def add_minutes_today(session: AsyncSession, gam: UserGamification, minutes: int) -> bool:
    """Adiciona minutos de prática hoje. Retorna True se meta diária atingida."""
    today = _today()
    if gam.last_minutes_date != today:
        gam.minutes_today = 0
        gam.last_minutes_date = today
    gam.minutes_today += minutes
    return gam.minutes_today >= gam.daily_goal_minutes


async def record_lesson_completion(
    session: AsyncSession,
    user_id: uuid.UUID,
    xp_earned: int,
) -> tuple[UserGamification, list[UserBadge]]:
    """Processa conclusão de lição: XP, streak, contadores, selos."""
    gam = await get_or_create_gamification(session, user_id)

    # Streak
    await update_streak(session, gam)

    # Contadores
    gam.total_lessons_completed += 1

    # XP
    _, _, _ = await add_xp(session, gam, xp_earned)

    # Streak badges
    streak_badges = await check_streak_badges(session, gam)

    # First lesson badge
    first_badges = await check_first_badges(session, gam, "first_lesson")

    # Streak day
    await ensure_streak_day(session, user_id, minutes=0, lessons=1)

    await session.flush()
    return gam, streak_badges + first_badges


async def record_conversation(session: AsyncSession, user_id: uuid.UUID) -> list[UserBadge]:
    """Registra uma conversa com tutor."""
    gam = await get_or_create_gamification(session, user_id)
    gam.total_conversations += 1
    badges = await check_conversation_badges(session, gam)
    await session.flush()
    return badges


async def record_flashcard_review(session: AsyncSession, user_id: uuid.UUID) -> None:
    """Registra revisão de flashcard."""
    gam = await get_or_create_gamification(session, user_id)
    gam.total_flashcards_reviewed += 1
    await session.flush()


async def ensure_weekly_league(session: AsyncSession, gam: UserGamification) -> None:
    """Garante que a liga semanal está inicializada para a semana atual."""
    today = _today()
    week_start = _week_start(today)
    if gam.league_week_start != week_start:
        # Nova semana: zera XP da semana e rank
        gam.league_week_start = week_start
        gam.league_xp_this_week = 0
        gam.league_rank = None


async def add_league_xp(session: AsyncSession, gam: UserGamification, xp: int) -> None:
    """Adiciona XP à liga semanal."""
    await ensure_weekly_league(session, gam)
    gam.league_xp_this_week += xp


async def finalize_weekly_league(
    session: AsyncSession, gam: UserGamification
) -> UserLeagueWeek | None:
    """Finaliza a semana anterior (chamado no início da nova semana)."""
    today = _today()
    last_week_start = _week_start(today - timedelta(days=1))
    if gam.league_week_start == last_week_start:
        return None  # já finalizada

    week = UserLeagueWeek(
        id=uuid7(),
        user_id=gam.user_id,
        week_start=last_week_start,
        tier=gam.league_tier,
        xp=gam.league_xp_this_week,
        rank=gam.league_rank,
    )
    session.add(week)
    return week


async def generate_daily_missions(
    session: AsyncSession, user_id: uuid.UUID
) -> Sequence[UserMission]:
    """Gera missões do dia (ou retorna existentes)."""
    today = _today()
    existing = list(
        await session.scalars(
            select(UserMission).where(UserMission.user_id == user_id, UserMission.day == today)
        )
    )
    if existing:
        return existing

    # Seleciona 3 missões aleatórias (peso por variedade)
    mission_pool = [
        (MissionType.COMPLETE_LESSON, 1, 10),
        (MissionType.REVIEW_FLASHCARDS, 10, 5),
        (MissionType.PRACTICE_SPEAKING, 3, 10),
        (MissionType.PRACTICE_LISTENING, 3, 10),
        (MissionType.PRACTICE_WRITING, 3, 10),
        (MissionType.USE_TUTOR, 1, 10),
        (MissionType.MAINTAIN_STREAK, 1, 5),
    ]
    selected = random.sample(mission_pool, k=min(3, len(mission_pool)))

    missions: list[UserMission] = []
    for mtype, target, xp_reward in selected:
        m = UserMission(
            id=uuid7(),
            user_id=user_id,
            day=today,
            type=mtype.value,
            target=target,
            xp_reward=xp_reward,
        )
        session.add(m)
        missions.append(m)
    await session.flush()
    return missions


async def update_mission_progress(
    session: AsyncSession,
    user_id: uuid.UUID,
    mission_type: MissionType,
    increment: int = 1,
) -> list[UserBadge]:
    """Atualiza progresso de missão e concede XP/badge se completada."""
    today = _today()
    mission = await session.scalar(
        select(UserMission).where(
            UserMission.user_id == user_id,
            UserMission.day == today,
            UserMission.type == mission_type.value,
        )
    )
    if not mission or mission.completed:
        return []

    mission.progress = min(mission.target, mission.progress + increment)
    new_badges: list[UserBadge] = []
    if mission.progress >= mission.target and not mission.completed:
        mission.completed = True
        gam = await get_or_create_gamification(session, user_id)
        _, _, _ = await add_xp(session, gam, mission.xp_reward)
        await add_league_xp(session, gam, mission.xp_reward)
    await session.flush()
    return new_badges
