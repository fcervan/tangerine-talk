"""Endpoints de gamificação: XP, streak, SRS, selos, ligas, missões (Fase 5)."""

from __future__ import annotations

import uuid
from datetime import date

from fastapi import APIRouter
from sqlalchemy import select

from ..auth.deps import CurrentUser, SessionDep
from ..gamification import service
from ..gamification.schemas import (
    BadgeOut,
    BadgeSlug,
    GamificationOut,
    LeaderboardEntry,
    LeaderboardOut,
    LeagueTier,
    LeagueWeekOut,
    MissionOut,
    MissionType,
    SRSItemOut,
    SRSReviewIn,
    SRSReviewOut,
    StreakDayOut,
)
from ..models import (
    User,
    UserBadge,
    UserGamification,
    UserLeagueWeek,
    UserMission,
    UserStreakDay,
)

router = APIRouter(tags=["gamification"])


@router.get("/gamification", response_model=GamificationOut)
async def get_gamification(user: CurrentUser, session: SessionDep) -> GamificationOut:
    """Resumo completo de gamificação do usuário."""
    gam = await service.get_or_create_gamification(session, user.id)
    await session.flush()  # garante que existe

    badges = list(
        await session.scalars(
            select(UserBadge)
            .where(UserBadge.user_id == user.id)
            .order_by(UserBadge.earned_at.desc())
        )
    )
    return GamificationOut(
        xp=gam.xp,
        level=gam.level,
        current_streak=gam.current_streak,
        longest_streak=gam.longest_streak,
        last_streak_date=gam.last_streak_date,
        streak_frozen=gam.streak_frozen,
        daily_goal_minutes=gam.daily_goal_minutes,
        minutes_today=gam.minutes_today,
        last_minutes_date=gam.last_minutes_date,
        league_tier=LeagueTier(gam.league_tier),
        league_xp_this_week=gam.league_xp_this_week,
        league_rank=gam.league_rank,
        league_week_start=gam.league_week_start,
        total_lessons_completed=gam.total_lessons_completed,
        total_conversations=gam.total_conversations,
        total_flashcards_reviewed=gam.total_flashcards_reviewed,
        badges=[
            BadgeOut(slug=BadgeSlug(b.slug), earned_at=b.earned_at, meta=b.meta) for b in badges
        ],
    )


@router.get("/gamification/streak", response_model=list[StreakDayOut])
async def get_streak_history(
    user: CurrentUser, session: SessionDep, days: int = 60
) -> list[StreakDayOut]:
    """Histórico de streak (últimos N dias)."""
    from datetime import date, timedelta

    cutoff = date.today() - timedelta(days=days)
    rows = list(
        await session.scalars(
            select(UserStreakDay)
            .where(UserStreakDay.user_id == user.id, UserStreakDay.day >= cutoff)
            .order_by(UserStreakDay.day.desc())
        )
    )
    return [
        StreakDayOut(day=r.day, minutes=r.minutes, lessons_completed=r.lessons_completed)
        for r in rows
    ]


@router.get("/gamification/badges", response_model=list[BadgeOut])
async def get_badges(user: CurrentUser, session: SessionDep) -> list[BadgeOut]:
    """Selos conquistados."""
    rows = list(
        await session.scalars(
            select(UserBadge)
            .where(UserBadge.user_id == user.id)
            .order_by(UserBadge.earned_at.desc())
        )
    )
    return [BadgeOut(slug=BadgeSlug(r.slug), earned_at=r.earned_at, meta=r.meta) for r in rows]


@router.get("/gamification/srs/due", response_model=list[SRSItemOut])
async def get_due_srs(user: CurrentUser, session: SessionDep, limit: int = 50) -> list[SRSItemOut]:
    """Itens vencidos para revisão (SRS)."""
    items = await service.get_due_srs(session, user.id, limit=limit)
    return [
        SRSItemOut(
            item_id=str(i.item_id),
            interval_days=i.interval_days,
            ease_factor=i.ease_factor,
            repetitions=i.repetitions,
            due_date=i.due_date,
            last_quality=i.last_quality,
            last_reviewed_at=i.last_reviewed_at,
        )
        for i in items
    ]


@router.post("/gamification/srs/review", response_model=SRSReviewOut)
async def review_srs_item(
    payload: SRSReviewIn, user: CurrentUser, session: SessionDep
) -> SRSReviewOut:
    """Registra revisão de item SRS."""
    item_id = uuid.UUID(payload.item_id)
    srs = await service.update_srs(session, user.id, item_id, payload.quality)
    # Próxima data de vencimento
    from ..gamification.service import sm2_next

    ef, interval, reps, due = sm2_next(
        srs.ease_factor, srs.interval_days, srs.repetitions, payload.quality
    )
    next_due = due
    return SRSReviewOut(
        item_id=payload.item_id,
        interval_days=srs.interval_days,
        ease_factor=srs.ease_factor,
        repetitions=srs.repetitions,
        due_date=srs.due_date,
        next_due=next_due,
    )


@router.get("/gamification/missions", response_model=list[MissionOut])
async def get_missions(user: CurrentUser, session: SessionDep) -> list[MissionOut]:
    """Missões do dia."""
    await service.generate_daily_missions(session, user.id)
    rows = list(
        await session.scalars(
            select(UserMission).where(
                UserMission.user_id == user.id, UserMission.day == date.today()
            )
        )
    )
    return [
        MissionOut(
            type=MissionType(r.type),
            target=r.target,
            progress=r.progress,
            completed=r.completed,
            xp_reward=r.xp_reward,
        )
        for r in rows
    ]


@router.get("/gamification/league/current", response_model=LeagueWeekOut)
async def get_current_league(user: CurrentUser, session: SessionDep) -> LeagueWeekOut:
    """Status da liga semanal atual."""
    gam = await service.get_or_create_gamification(session, user.id)
    await service.ensure_weekly_league(session, gam)
    return LeagueWeekOut(
        week_start=gam.league_week_start or date.today(),
        tier=LeagueTier(gam.league_tier),
        xp=gam.league_xp_this_week,
        rank=gam.league_rank,
        promoted=False,
        demoted=False,
    )


@router.get("/gamification/league/history", response_model=list[LeagueWeekOut])
async def get_league_history(user: CurrentUser, session: SessionDep) -> list[LeagueWeekOut]:
    """Histórico de ligas semanais."""
    rows = list(
        await session.scalars(
            select(UserLeagueWeek)
            .where(UserLeagueWeek.user_id == user.id)
            .order_by(UserLeagueWeek.week_start.desc())
        )
    )
    return [
        LeagueWeekOut(
            week_start=r.week_start,
            tier=LeagueTier(r.tier),
            xp=r.xp,
            rank=r.rank,
            promoted=r.promoted,
            demoted=r.demoted,
        )
        for r in rows
    ]


@router.get("/gamification/leaderboard", response_model=LeaderboardOut)
async def get_leaderboard(
    user: CurrentUser, session: SessionDep, week_start: date | None = None
) -> LeaderboardOut:
    """Ranking da liga semanal (top 50)."""
    if week_start is None:
        from datetime import date, timedelta

        week_start = date.today() - timedelta(days=date.today().weekday())

    # Busca usuários da mesma tier e semana
    gam = await service.get_or_create_gamification(session, user.id)
    await service.ensure_weekly_league(session, gam)

    rows = await session.execute(
        select(UserGamification, User.name)
        .join(User, User.id == UserGamification.user_id)
        .where(
            UserGamification.league_tier == gam.league_tier,
            UserGamification.league_week_start == week_start,
        )
        .order_by(UserGamification.league_xp_this_week.desc())
        .limit(50)
    )
    entries = [
        LeaderboardEntry(user_id=str(g.user_id), name=name, xp=g.league_xp_this_week, rank=i + 1)
        for i, (g, name) in enumerate(rows.all())
    ]
    return LeaderboardOut(week_start=week_start, tier=LeagueTier(gam.league_tier), entries=entries)
