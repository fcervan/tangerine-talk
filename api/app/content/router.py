"""Rotas de trilha, lições e baralhos oficiais.

Progresso é sempre do usuário autenticado. Glossas seguem o idioma da interface
do usuário, com fallback por base BCP-47 e, por último, pt-BR — nunca inglês.
"""

from __future__ import annotations

import uuid
from collections import defaultdict
from typing import Annotated

from fastapi import APIRouter, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from ..auth.deps import CurrentUser, SessionDep
from ..gamification import service as gamification_service
from ..i18n import DEFAULT_LOCALE, base_language, normalize_locale
from ..models import (
    Deck,
    DeckItem,
    Exercise,
    Item,
    ItemTranslation,
    Lesson,
    Unit,
    User,
    UserLessonProgress,
)
from ..models.base import utcnow
from .schemas import (
    CompleteIn,
    CompleteOut,
    CurriculumLanguagesOut,
    CurriculumOut,
    DeckListOut,
    DeckOut,
    ExerciseOut,
    ItemOut,
    LessonDetailOut,
    LessonOut,
    LessonStatus,
    UnitDetailOut,
    UnitOut,
)

router = APIRouter(tags=["content"])


def _locale(user: User) -> str:
    try:
        return normalize_locale(user.ui_language)
    except ValueError:
        return DEFAULT_LOCALE


def _target_language(user: User, provided: str | None) -> str:
    raw = (provided or user.target_language or "").strip()
    if not raw:
        raise HTTPException(
            status_code=400,
            detail="Defina o idioma estudado no onboarding ou informe ?target_language=.",
        )
    try:
        return normalize_locale(raw)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from None


def _gloss(
    translations: dict[str, dict[str, str]],
    item_id: uuid.UUID,
    locale: str,
    default: str,
) -> tuple[str, str]:
    """Exata → mesma base → pt-BR → primeiro disponível → texto original."""
    row = translations.get(str(item_id), {})
    if locale in row:
        return row[locale], locale
    base = base_language(locale)
    for key, value in row.items():
        if base_language(key) == base:
            return value, key
    if DEFAULT_LOCALE in row:
        return row[DEFAULT_LOCALE], DEFAULT_LOCALE
    if row:
        key = sorted(row)[0]
        return row[key], key
    return default, "und"


async def _translations(
    session: AsyncSession, item_ids: list[uuid.UUID]
) -> dict[str, dict[str, str]]:
    if not item_ids:
        return {}
    rows = await session.scalars(
        select(ItemTranslation).where(ItemTranslation.item_id.in_(item_ids))
    )
    result: dict[str, dict[str, str]] = defaultdict(dict)
    for row in rows:
        result[str(row.item_id)][row.locale] = row.gloss
    return dict(result)


def _item_out(item: Item, translations: dict[str, dict[str, str]], locale: str) -> ItemOut:
    gloss, gloss_locale = _gloss(translations, item.id, locale, item.front_text)
    return ItemOut(
        id=item.id,
        kind=item.kind,
        front_text=item.front_text,
        example=item.example,
        gloss=gloss,
        gloss_locale=gloss_locale,
    )


def _exercise_out(
    exercise: Exercise, translations: dict[str, dict[str, str]], locale: str
) -> ExerciseOut:
    prompt, answer = exercise.prompt, exercise.answer
    if exercise.item_id is not None and exercise.type in {"flashcard", "translation"}:
        gloss, _ = _gloss(translations, exercise.item_id, locale, exercise.answer)
        if exercise.type == "flashcard":
            answer = gloss
        else:
            prompt = gloss
    return ExerciseOut(
        id=exercise.id,
        type=exercise.type,
        prompt=prompt,
        answer=answer,
        options=exercise.options,
        order_index=exercise.order_index,
    )


async def _published_units(session: AsyncSession, target: str) -> list[Unit]:
    return list(
        await session.scalars(
            select(Unit)
            .where(Unit.target_language == target, Unit.is_published.is_(True))
            .order_by(Unit.order_index)
        )
    )


async def _completed_ids(
    session: AsyncSession, user_id: uuid.UUID, lesson_ids: list[uuid.UUID]
) -> set[uuid.UUID]:
    if not lesson_ids:
        return set()
    rows = await session.scalars(
        select(UserLessonProgress.lesson_id).where(
            UserLessonProgress.user_id == user_id,
            UserLessonProgress.lesson_id.in_(lesson_ids),
        )
    )
    return set(rows)


def _unit_statuses(
    units: list[Unit],
    lessons_by_unit: dict[uuid.UUID, list[Lesson]],
    completed: set[uuid.UUID],
) -> dict[uuid.UUID, LessonStatus]:
    """Pré-requisito fecha o nó até que todas as lições anteriores terminem."""
    done_units: set[uuid.UUID] = set()
    result: dict[uuid.UUID, LessonStatus] = {}
    for unit in units:
        lesson_ids = [lesson.id for lesson in lessons_by_unit.get(unit.id, [])]
        finished = bool(lesson_ids) and all(lesson_id in completed for lesson_id in lesson_ids)
        prerequisite_ok = unit.prerequisite_id is None or unit.prerequisite_id in done_units
        if finished:
            result[unit.id] = "completed"
            done_units.add(unit.id)
        elif prerequisite_ok:
            result[unit.id] = "available"
        else:
            result[unit.id] = "locked"
    return result


def _lesson_out(
    lesson: Lesson, unit_status: LessonStatus, completed: set[uuid.UUID], count: int
) -> LessonOut:
    lesson_status: LessonStatus = (
        "completed"
        if lesson.id in completed
        else ("locked" if unit_status == "locked" else "available")
    )
    return LessonOut(
        id=lesson.id,
        slug=lesson.slug,
        title=lesson.title,
        order_index=lesson.order_index,
        kind=lesson.kind,
        xp_reward=lesson.xp_reward,
        status=lesson_status,
        exercise_count=count,
    )


async def _exercise_counts(
    session: AsyncSession, lesson_ids: list[uuid.UUID]
) -> dict[uuid.UUID, int]:
    if not lesson_ids:
        return {}
    rows = await session.execute(
        select(Exercise.lesson_id, func.count())
        .where(Exercise.lesson_id.in_(lesson_ids))
        .group_by(Exercise.lesson_id)
    )
    return {lesson_id: int(count) for lesson_id, count in rows.all()}


@router.get("/curriculum/languages", response_model=CurriculumLanguagesOut)
async def curriculum_languages(user: CurrentUser, session: SessionDep) -> CurriculumLanguagesOut:
    """Idiomas que têm conteúdo publicado — a lista cresce com o seed."""
    rows = await session.scalars(
        select(Unit.target_language)
        .where(Unit.is_published.is_(True))
        .distinct()
        .order_by(Unit.target_language)
    )
    return CurriculumLanguagesOut(languages=list(rows))


@router.get("/curriculum", response_model=CurriculumOut)
async def curriculum(
    user: CurrentUser,
    session: SessionDep,
    target_language: Annotated[str | None, Query()] = None,
) -> CurriculumOut:
    target = _target_language(user, target_language)
    units = await _published_units(session, target)
    unit_ids = [unit.id for unit in units]
    lessons = (
        list(
            await session.scalars(
                select(Lesson)
                .where(Lesson.unit_id.in_(unit_ids), Lesson.is_published.is_(True))
                .order_by(Lesson.order_index)
            )
        )
        if unit_ids
        else []
    )
    lessons_by_unit: dict[uuid.UUID, list[Lesson]] = defaultdict(list)
    for lesson in lessons:
        lessons_by_unit[lesson.unit_id].append(lesson)
    completed = await _completed_ids(session, user.id, [lesson.id for lesson in lessons])
    counts = await _exercise_counts(session, [lesson.id for lesson in lessons])
    statuses = _unit_statuses(units, lessons_by_unit, completed)

    return CurriculumOut(
        target_language=target,
        level=user.settings.get("level") if isinstance(user.settings, dict) else None,
        locale=_locale(user),
        units=[
            UnitOut(
                id=unit.id,
                target_language=unit.target_language,
                level=unit.level,
                slug=unit.slug,
                title=unit.title,
                description=unit.description,
                order_index=unit.order_index,
                status=statuses[unit.id],
                lessons=[
                    _lesson_out(lesson, statuses[unit.id], completed, counts.get(lesson.id, 0))
                    for lesson in lessons_by_unit.get(unit.id, [])
                ],
            )
            for unit in units
        ],
    )


async def _load_lesson(
    session: AsyncSession, lesson_id: uuid.UUID, user_id: uuid.UUID
) -> tuple[Lesson, LessonStatus]:
    lesson = await session.scalar(
        select(Lesson).where(Lesson.id == lesson_id, Lesson.is_published.is_(True))
    )
    if lesson is None:
        raise HTTPException(status_code=404, detail="Lição não encontrada.")
    unit = await session.get(Unit, lesson.unit_id)
    if unit is None or not unit.is_published:
        raise HTTPException(status_code=404, detail="Unidade não encontrada.")

    units = await _published_units(session, unit.target_language)
    unit_ids = [row.id for row in units]
    all_lessons = (
        list(
            await session.scalars(
                select(Lesson).where(Lesson.unit_id.in_(unit_ids), Lesson.is_published.is_(True))
            )
        )
        if unit_ids
        else []
    )
    by_unit: dict[uuid.UUID, list[Lesson]] = defaultdict(list)
    for row in all_lessons:
        by_unit[row.unit_id].append(row)
    statuses = _unit_statuses(
        units, by_unit, await _completed_ids(session, user_id, [row.id for row in all_lessons])
    )
    return lesson, statuses[unit.id]


@router.get("/curriculum/units/{unit_id}", response_model=UnitDetailOut)
async def unit_detail(unit_id: uuid.UUID, user: CurrentUser, session: SessionDep) -> UnitDetailOut:
    unit = await session.scalar(select(Unit).where(Unit.id == unit_id, Unit.is_published.is_(True)))
    if unit is None:
        raise HTTPException(status_code=404, detail="Unidade não encontrada.")

    lessons = list(
        await session.scalars(
            select(Lesson)
            .where(Lesson.unit_id == unit.id, Lesson.is_published.is_(True))
            .order_by(Lesson.order_index)
        )
    )
    all_units = await _published_units(session, unit.target_language)
    all_ids = [row.id for row in all_units]
    all_lessons = (
        list(
            await session.scalars(
                select(Lesson).where(Lesson.unit_id.in_(all_ids), Lesson.is_published.is_(True))
            )
        )
        if all_ids
        else []
    )
    by_unit: dict[uuid.UUID, list[Lesson]] = defaultdict(list)
    for row in all_lessons:
        by_unit[row.unit_id].append(row)
    completed = await _completed_ids(session, user.id, [row.id for row in all_lessons])
    statuses = _unit_statuses(all_units, by_unit, completed)
    counts = await _exercise_counts(session, [row.id for row in lessons])

    lesson_ids = [lesson.id for lesson in lessons]
    items = (
        list(
            await session.scalars(
                select(Item).where(Item.lesson_id.in_(lesson_ids)).order_by(Item.order_index)
            )
        )
        if lesson_ids
        else []
    )
    locale = _locale(user)
    translations = await _translations(session, [item.id for item in items])
    return UnitDetailOut(
        id=unit.id,
        target_language=unit.target_language,
        level=unit.level,
        slug=unit.slug,
        title=unit.title,
        description=unit.description,
        order_index=unit.order_index,
        status=statuses[unit.id],
        lessons=[
            _lesson_out(lesson, statuses[unit.id], completed, counts.get(lesson.id, 0))
            for lesson in lessons
        ],
        items=[_item_out(item, translations, locale) for item in items],
    )


@router.get("/curriculum/lessons/{lesson_id}", response_model=LessonDetailOut)
async def lesson_detail(
    lesson_id: uuid.UUID, user: CurrentUser, session: SessionDep
) -> LessonDetailOut:
    lesson, unit_status = await _load_lesson(session, lesson_id, user.id)
    if unit_status == "locked":
        raise HTTPException(
            status_code=403, detail="Conclua a unidade anterior para abrir esta lição."
        )
    completed = await _completed_ids(session, user.id, [lesson.id])
    item_list = list(
        await session.scalars(
            select(Item).where(Item.lesson_id == lesson.id).order_by(Item.order_index)
        )
    )
    exercises = list(
        await session.scalars(
            select(Exercise).where(Exercise.lesson_id == lesson.id).order_by(Exercise.order_index)
        )
    )
    item_ids = [item.id for item in item_list] + [
        exercise.item_id for exercise in exercises if exercise.item_id is not None
    ]
    locale = _locale(user)
    translations = await _translations(session, item_ids)
    counts = await _exercise_counts(session, [lesson.id])
    return LessonDetailOut(
        **_lesson_out(lesson, unit_status, completed, counts.get(lesson.id, 0)).model_dump(),
        items=[_item_out(item, translations, locale) for item in item_list],
        exercises=[_exercise_out(row, translations, locale) for row in exercises],
    )


@router.post("/curriculum/lessons/{lesson_id}/complete", response_model=CompleteOut)
async def complete_lesson(
    lesson_id: uuid.UUID,
    payload: CompleteIn,
    user: CurrentUser,
    session: SessionDep,
) -> CompleteOut:
    lesson, unit_status = await _load_lesson(session, lesson_id, user.id)
    if unit_status == "locked":
        raise HTTPException(
            status_code=403, detail="Conclua a unidade anterior para abrir esta lição."
        )
    existing = await session.scalar(
        select(UserLessonProgress).where(
            UserLessonProgress.user_id == user.id,
            UserLessonProgress.lesson_id == lesson.id,
        )
    )
    if existing is not None:
        return CompleteOut(
            lesson_id=lesson.id,
            status="already_completed",
            xp_earned=0,
            completed_at=existing.completed_at,
        )

    progress = UserLessonProgress(
        user_id=user.id, lesson_id=lesson.id, score=payload.score, completed_at=utcnow()
    )
    session.add(progress)

    # Gamificação: XP, streak, selos (antes do commit para mesma transação)
    await gamification_service.record_lesson_completion(session, user.id, lesson.xp_reward)

    await session.commit()

    return CompleteOut(
        lesson_id=lesson.id,
        status="completed",
        xp_earned=lesson.xp_reward,
        completed_at=progress.completed_at,
    )


@router.get("/decks", response_model=DeckListOut)
async def list_decks(
    user: CurrentUser,
    session: SessionDep,
    target_language: Annotated[str | None, Query()] = None,
) -> DeckListOut:
    target = _target_language(user, target_language)
    decks = list(
        await session.scalars(
            select(Deck)
            .where(Deck.target_language == target, Deck.is_official.is_(True))
            .order_by(Deck.title)
        )
    )
    deck_ids = [deck.id for deck in decks]
    counts: dict[uuid.UUID, int] = defaultdict(int)
    if deck_ids:
        rows = await session.execute(
            select(DeckItem.deck_id, func.count())
            .where(DeckItem.deck_id.in_(deck_ids))
            .group_by(DeckItem.deck_id)
        )
        counts = {deck_id: int(count) for deck_id, count in rows.all()}
    return DeckListOut(
        target_language=target,
        decks=[
            DeckOut(
                id=deck.id,
                slug=deck.slug,
                title=deck.title,
                description=deck.description,
                level=deck.level,
                item_count=counts.get(deck.id, 0),
            )
            for deck in decks
        ],
    )


@router.get("/decks/{deck_id}", response_model=DeckOut)
async def deck_detail(deck_id: uuid.UUID, user: CurrentUser, session: SessionDep) -> DeckOut:
    deck = await session.scalar(select(Deck).where(Deck.id == deck_id, Deck.is_official.is_(True)))
    if deck is None:
        raise HTTPException(status_code=404, detail="Baralho não encontrado.")
    rows = await session.execute(
        select(Item)
        .join(DeckItem, DeckItem.item_id == Item.id)
        .where(DeckItem.deck_id == deck.id)
        .order_by(Item.order_index, Item.front_text)
    )
    items = list(rows.scalars())
    locale = _locale(user)
    translations = await _translations(session, [item.id for item in items])
    return DeckOut(
        id=deck.id,
        slug=deck.slug,
        title=deck.title,
        description=deck.description,
        level=deck.level,
        item_count=len(items),
        items=[_item_out(item, translations, locale) for item in items],
    )
