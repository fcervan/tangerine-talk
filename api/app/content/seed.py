"""Conteúdo oficial versionado em código — a fonte da verdade é o MySQL.

Não é upload, não é planilha, não é segredo: um conjunto pequeno e auditável de
unidades, lições, itens e exercícios. Aplicar de novo é seguro (`seed_content`
verifica o slug da unidade antes de gravar). Glossas ficam em `item_translations`;
a frase estudada permanece sempre no idioma alvo.
"""

from __future__ import annotations

from typing import TypedDict

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models import Deck, DeckItem, Exercise, Item, ItemTranslation, Lesson, Unit
from ..models.base import uuid7


class ItemSpec(TypedDict):
    key: str
    kind: str
    front_text: str
    example: str
    glosses: dict[str, str]


class ExerciseSpec(TypedDict):
    type: str
    item: str
    prompt: str
    answer: str
    options: list[str] | None
    order: int


class LessonSpec(TypedDict):
    slug: str
    title: str
    order: int
    xp: int
    items: list[str]
    exercises: list[ExerciseSpec]


class UnitSpec(TypedDict):
    slug: str
    title: str
    description: str
    level: str
    order: int
    prerequisite: str | None
    lessons: list[LessonSpec]


class DeckSpec(TypedDict):
    slug: str
    title: str
    description: str
    level: str
    items: list[str]


ITEMS: list[ItemSpec] = [
    {
        "key": "hola",
        "kind": "word",
        "front_text": "Hola",
        "example": "Hola, María.",
        "glosses": {"pt-BR": "Olá", "en-US": "Hello"},
    },
    {
        "key": "buenos_dias",
        "kind": "phrase",
        "front_text": "Buenos días",
        "example": "Buenos días, profesor.",
        "glosses": {"pt-BR": "Bom dia", "en-US": "Good morning"},
    },
    {
        "key": "buenas_tardes",
        "kind": "phrase",
        "front_text": "Buenas tardes",
        "example": "Buenas tardes, ¿cómo estás?",
        "glosses": {"pt-BR": "Boa tarde", "en-US": "Good afternoon"},
    },
    {
        "key": "como_estas",
        "kind": "phrase",
        "front_text": "¿Cómo estás?",
        "example": "¿Cómo estás? — Muy bien, gracias.",
        "glosses": {"pt-BR": "Como você está?", "en-US": "How are you?"},
    },
    {
        "key": "mucho_gusto",
        "kind": "phrase",
        "front_text": "Mucho gusto",
        "example": "Mucho gusto en conocerte.",
        "glosses": {"pt-BR": "Prazer em conhecê-lo", "en-US": "Nice to meet you"},
    },
    {
        "key": "gracias",
        "kind": "word",
        "front_text": "Gracias",
        "example": "Gracias por tu ayuda.",
        "glosses": {"pt-BR": "Obrigado", "en-US": "Thank you"},
    },
    {
        "key": "uno",
        "kind": "word",
        "front_text": "Uno",
        "example": "Tengo uno.",
        "glosses": {"pt-BR": "Um", "en-US": "One"},
    },
    {
        "key": "dos",
        "kind": "word",
        "front_text": "Dos",
        "example": "Dos libros.",
        "glosses": {"pt-BR": "Dois", "en-US": "Two"},
    },
    {
        "key": "tres",
        "kind": "word",
        "front_text": "Tres",
        "example": "Tres amigos.",
        "glosses": {"pt-BR": "Três", "en-US": "Three"},
    },
    {
        "key": "cuatro",
        "kind": "word",
        "front_text": "Cuatro",
        "example": "Cuatro sillas.",
        "glosses": {"pt-BR": "Quatro", "en-US": "Four"},
    },
]

UNITS: list[UnitSpec] = [
    {
        "slug": "saudacoes",
        "title": "Saudações",
        "description": "Cumprimentos e primeiras apresentações em espanhol.",
        "level": "A1",
        "order": 1,
        "prerequisite": None,
        "lessons": [
            {
                "slug": "primeiras-saudacoes",
                "title": "Primeiras saudações",
                "order": 1,
                "xp": 10,
                "items": ["hola", "buenos_dias", "buenas_tardes", "gracias"],
                "exercises": [
                    {
                        "type": "flashcard",
                        "item": "hola",
                        "prompt": "Hola",
                        "answer": "Olá",
                        "options": None,
                        "order": 1,
                    },
                    {
                        "type": "flashcard",
                        "item": "buenos_dias",
                        "prompt": "Buenos días",
                        "answer": "Bom dia",
                        "options": None,
                        "order": 2,
                    },
                    {
                        "type": "multiple_choice",
                        "item": "gracias",
                        "prompt": "Você agradece em espanhol dizendo:",
                        "answer": "Gracias",
                        "options": ["Gracias", "Hola", "Tres"],
                        "order": 3,
                    },
                ],
            },
            {
                "slug": "apresentacoes",
                "title": "Apresentações",
                "order": 2,
                "xp": 10,
                "items": ["como_estas", "mucho_gusto"],
                "exercises": [
                    {
                        "type": "translation",
                        "item": "como_estas",
                        "prompt": "Como você está?",
                        "answer": "¿Cómo estás?",
                        "options": None,
                        "order": 1,
                    },
                    {
                        "type": "multiple_choice",
                        "item": "mucho_gusto",
                        "prompt": "Ao conhecer alguém, diga:",
                        "answer": "Mucho gusto",
                        "options": ["Mucho gusto", "Buenas tardes", "Dos"],
                        "order": 2,
                    },
                ],
            },
        ],
    },
    {
        "slug": "numeros",
        "title": "Números",
        "description": "Os primeiros números para se virar no dia a dia.",
        "level": "A1",
        "order": 2,
        "prerequisite": "saudacoes",
        "lessons": [
            {
                "slug": "numeros-um-a-quatro",
                "title": "Números de um a quatro",
                "order": 1,
                "xp": 10,
                "items": ["uno", "dos", "tres", "cuatro"],
                "exercises": [
                    {
                        "type": "flashcard",
                        "item": "uno",
                        "prompt": "Uno",
                        "answer": "Um",
                        "options": None,
                        "order": 1,
                    },
                    {
                        "type": "multiple_choice",
                        "item": "dos",
                        "prompt": "Qual palavra significa «dois» em espanhol?",
                        "answer": "Dos",
                        "options": ["Dos", "Uno", "Cuatro"],
                        "order": 2,
                    },
                    {
                        "type": "translation",
                        "item": "tres",
                        "prompt": "Três",
                        "answer": "Tres",
                        "options": None,
                        "order": 3,
                    },
                ],
            },
        ],
    },
]

DECKS: list[DeckSpec] = [
    {
        "slug": "essencial-a1",
        "title": "Espanhol A1 — essencial",
        "description": "Saudações e números para os primeiros dias.",
        "level": "A1",
        "items": [item["key"] for item in ITEMS],
    }
]

TARGET_LANGUAGE = "es"


async def seed_content(
    session: AsyncSession, *, target_language: str = TARGET_LANGUAGE
) -> dict[str, int]:
    """Cria o conteúdo oficial uma vez. Devolve contagens para o CLI/testes."""
    existing = await session.scalar(
        select(Unit.id).where(Unit.target_language == target_language).limit(1)
    )
    if existing is not None:
        return {"units": 0, "lessons": 0, "items": 0, "exercises": 0, "decks": 0}

    total = {"units": 0, "lessons": 0, "items": 0, "exercises": 0, "decks": 0}
    unit_by_slug: dict[str, Unit] = {}
    lesson_by_slug: dict[str, Lesson] = {}

    # 1. Unidades primeiro. O FK self-referencial de prerequisite exige dois
    #    flushes: inserir sem pai e só depois ligar os pré-requisitos.
    for unit_spec in UNITS:
        unit = Unit(
            id=uuid7(),
            target_language=target_language,
            level=unit_spec["level"],
            slug=unit_spec["slug"],
            title=unit_spec["title"],
            description=unit_spec["description"],
            order_index=unit_spec["order"],
            is_published=True,
        )
        session.add(unit)
        unit_by_slug[unit.slug] = unit
        total["units"] += 1
    await session.flush()

    for unit_spec in UNITS:
        prerequisite = unit_spec["prerequisite"]
        if prerequisite is not None:
            unit_by_slug[unit_spec["slug"]].prerequisite_id = unit_by_slug[
                prerequisite
            ].id
    await session.flush()

    # 2. Lições: os itens apontam para elas.
    for unit_spec in UNITS:
        unit = unit_by_slug[unit_spec["slug"]]
        for lesson_spec in unit_spec["lessons"]:
            lesson = Lesson(
                id=uuid7(),
                unit_id=unit.id,
                slug=lesson_spec["slug"],
                title=lesson_spec["title"],
                order_index=lesson_spec["order"],
                kind="lesson",
                xp_reward=lesson_spec["xp"],
                is_published=True,
            )
            session.add(lesson)
            lesson_by_slug[lesson.slug] = lesson
            total["lessons"] += 1
    await session.flush()

    # 3. Itens e glossas, já com a lição correta e a ordem dentro dela.
    item_lesson: dict[str, tuple[Lesson, int]] = {}
    for unit_spec in UNITS:
        for lesson_spec in unit_spec["lessons"]:
            lesson = lesson_by_slug[lesson_spec["slug"]]
            for index, key in enumerate(lesson_spec["items"], start=1):
                item_lesson[key] = (lesson, index)

    items_by_key: dict[str, Item] = {}
    for item_spec in ITEMS:
        lesson, index = item_lesson[item_spec["key"]]
        item = Item(
            id=uuid7(),
            lesson_id=lesson.id,
            kind=item_spec["kind"],
            front_text=item_spec["front_text"],
            example=item_spec["example"],
            order_index=index,
        )
        items_by_key[item_spec["key"]] = item
        session.add(item)
        total["items"] += 1
        for locale, gloss in item_spec["glosses"].items():
            session.add(ItemTranslation(item_id=item.id, locale=locale, gloss=gloss))
    await session.flush()

    # 4. Exercícios e baralhos, depois de todos os itens persistidos.
    for unit_spec in UNITS:
        for lesson_spec in unit_spec["lessons"]:
            lesson = lesson_by_slug[lesson_spec["slug"]]
            for exercise_spec in lesson_spec["exercises"]:
                session.add(
                    Exercise(
                        id=uuid7(),
                        lesson_id=lesson.id,
                        item_id=items_by_key[exercise_spec["item"]].id,
                        type=exercise_spec["type"],
                        prompt=exercise_spec["prompt"],
                        answer=exercise_spec["answer"],
                        options=exercise_spec["options"],
                        order_index=exercise_spec["order"],
                    )
                )
                total["exercises"] += 1

    for deck_spec in DECKS:
        deck = Deck(
            id=uuid7(),
            target_language=target_language,
            level=deck_spec["level"],
            slug=deck_spec["slug"],
            title=deck_spec["title"],
            description=deck_spec["description"],
            is_official=True,
        )
        session.add(deck)
        for key in deck_spec["items"]:
            session.add(DeckItem(deck_id=deck.id, item_id=items_by_key[key].id))
        total["decks"] += 1

    await session.commit()
    return total
