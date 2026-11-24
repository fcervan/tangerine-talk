"""Sincronização MySQL → Qdrant via outbox (Fase 6).

MySQL é a fonte da verdade; Qdrant é índice derivado e reconstruível.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Any

from qdrant_client.models import (
    Distance,
    HnswConfigDiff,
    PayloadSchemaType,
    PointStruct,
    VectorParams,
)
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..config import settings
from ..models import ContentOutbox, Deck, Item, Lesson, OutboxEventType, Unit
from ..models.base import utcnow
from .client import get_qdrant_client
from .embed import embed_hybrid

COLLECTION_NAME = f"content_v1_{settings.embedding_model.replace('/', '_').replace('-', '_')}"
EMBEDDING_DIM = settings.embedding_dim


async def ensure_collection() -> None:
    """Cria a coleção Qdrant se não existir."""
    client = get_qdrant_client()
    exists = await client.collection_exists(COLLECTION_NAME)
    if exists:
        return

    await client.create_collection(
        collection_name=COLLECTION_NAME,
        vectors_config={
            "dense": VectorParams(size=EMBEDDING_DIM, distance=Distance.COSINE)
        },
        hnsw_config=HnswConfigDiff(m=16, ef_construct=100),
    )
    # Índices para filtros
    await client.create_payload_index(
        COLLECTION_NAME, field_name="target_language", field_schema=PayloadSchemaType.KEYWORD
    )
    await client.create_payload_index(
        COLLECTION_NAME, field_name="language", field_schema=PayloadSchemaType.KEYWORD
    )
    await client.create_payload_index(
        COLLECTION_NAME, field_name="level", field_schema=PayloadSchemaType.KEYWORD
    )
    await client.create_payload_index(
        COLLECTION_NAME, field_name="item_type", field_schema=PayloadSchemaType.KEYWORD
    )
    await client.create_payload_index(
        COLLECTION_NAME, field_name="item_id", field_schema=PayloadSchemaType.KEYWORD
    )
    await client.create_payload_index(
        COLLECTION_NAME, field_name="deck_id", field_schema=PayloadSchemaType.KEYWORD
    )
    await client.create_payload_index(
        COLLECTION_NAME, field_name="user_id", field_schema=PayloadSchemaType.KEYWORD
    )


async def _build_item_payload(
    session: AsyncSession, item: Item, target_language: str
) -> dict[str, Any]:
    """Constrói payload do item para Qdrant."""
    from sqlalchemy import select

    from ..models import ItemTranslation

    glosses = dict(
        await session.execute(
            select(ItemTranslation.locale, ItemTranslation.gloss).where(
                ItemTranslation.item_id == item.id
            )
        )
    )

    # Busca a unit do item via lesson
    unit = None
    if item.lesson_id:
        lesson = await session.get(Lesson, item.lesson_id)
        if lesson and lesson.unit_id:
            unit = await session.get(Unit, lesson.unit_id)

    language = unit.target_language if unit else target_language
    level = unit.level if unit else "A1"

    return {
        "item_id": str(item.id),
        "target_language": target_language,
        "language": language,
        "level": level,
        "item_type": item.kind,
        "front_text": item.front_text,
        "example": item.example,
        "gloss_pt_br": glosses.get("pt-BR"),
        "gloss_en_us": glosses.get("en-US"),
    }


async def _build_deck_payload(
    session: AsyncSession, deck: Deck, items: list[Item]
) -> dict[str, Any]:
    """Constrói payload do deck para Qdrant."""
    item_payloads = []
    for item in items:
        item_payloads.append(await _build_item_payload(session, item, deck.target_language))

    return {
        "deck_id": str(deck.id),
        "target_language": deck.target_language,
        "level": deck.level,
        "title": deck.title,
        "description": deck.description,
        "item_count": len(items),
        "is_official": deck.is_official,
        "user_id": str(deck.user_id) if deck.user_id else None,
        "items": item_payloads,
    }


async def upsert_item(
    session: AsyncSession, item: Item, target_language: str
) -> None:
    """Upsert de um item no Qdrant."""
    await ensure_collection()
    client = get_qdrant_client()

    payload = await _build_item_payload(session, item, target_language)
    # Texto para embedding: front_text + example + glossas
    text_parts = [item.front_text]
    if item.example:
        text_parts.append(item.example)
    for k in ("gloss_pt_br", "gloss_en_us"):
        if payload.get(k):
            text_parts.append(payload[k])
    text = " ".join(text_parts)

    dense, _ = embed_hybrid([text])  # Use apenas dense por enquanto
    point = PointStruct(
        id=str(item.id),
        vector={"dense": dense[0].tolist()},
        payload=payload,
    )

    await client.upsert(collection_name=COLLECTION_NAME, points=[point])


async def upsert_deck(session: AsyncSession, deck: Deck) -> None:
    """Upsert de um deck no Qdrant (inclui itens)."""
    from sqlalchemy import select

    from ..models import DeckItem

    items = list(
        await session.scalars(
            select(Item)
            .join(DeckItem, DeckItem.item_id == Item.id)
            .where(DeckItem.deck_id == deck.id)
            .order_by(Item.order_index)
        )
    )
    payload = await _build_deck_payload(session, deck, items)

    # Embedding do deck: título + descrição + itens
    text_parts = [deck.title]
    if deck.description:
        text_parts.append(deck.description)
    for item in items:
        text_parts.append(item.front_text)
    text = " ".join(text_parts)

    dense, _ = embed_hybrid([text])  # Use apenas dense por enquanto
    point = PointStruct(
        id=str(deck.id),
        vector={"dense": dense[0].tolist()},
        payload=payload,
    )

    client = get_qdrant_client()
    await client.upsert(collection_name=COLLECTION_NAME, points=[point])


async def delete_item(entity_id: uuid.UUID) -> None:
    """Remove item do Qdrant."""
    client = get_qdrant_client()
    await client.delete(
        collection_name=COLLECTION_NAME,
        points_selector=[str(entity_id)],
    )


async def delete_deck(entity_id: uuid.UUID) -> None:
    """Remove deck do Qdrant."""
    client = get_qdrant_client()
    await client.delete(
        collection_name=COLLECTION_NAME,
        points_selector=[str(entity_id)],
    )


async def sync_outbox(
    session: AsyncSession, batch_size: int = 100
) -> int:
    """Processa eventos do outbox e aplica no Qdrant.

    Retorna número de eventos processados.
    """
    # Busca eventos não processados
    events = list(
        await session.scalars(
            select(ContentOutbox)
            .where(ContentOutbox.processed_at.is_(None))
            .order_by(ContentOutbox.created_at)
            .limit(batch_size)
        )
    )

    if not events:
        return 0

    processed = 0
    for event in events:
        try:
            if event.event_type == OutboxEventType.ITEM_UPSERT:
                item = await session.get(Item, event.entity_id)
                if item:
                    await upsert_item(session, item, event.target_language)
            elif event.event_type == OutboxEventType.ITEM_DELETE:
                await delete_item(event.entity_id)
            elif event.event_type == OutboxEventType.DECK_UPSERT:
                deck = await session.get(Deck, event.entity_id)
                if deck:
                    await upsert_deck(session, deck)
            elif event.event_type == OutboxEventType.DECK_DELETE:
                await delete_deck(event.entity_id)

            event.processed_at = utcnow()
            processed += 1
        except Exception as exc:
            event.attempts += 1
            event.last_error = str(exc)[:500]
            if event.attempts >= 5:
                event.processed_at = utcnow()  # Marca como processado para não travar
        await session.flush()

    return processed


async def reindex_all(session: AsyncSession) -> int:
    """Reindexação completa (blue/green): cria nova coleção e popula.

    Para uso em mudança de modelo de embedding ou recuperação.
    """
    client = get_qdrant_client()

    # Cria nova coleção com sufixo de versão
    new_collection = f"{COLLECTION_NAME}_{int(datetime.now(UTC).timestamp())}"

    await client.create_collection(
        collection_name=new_collection,
        vectors_config={
            "dense": VectorParams(size=EMBEDDING_DIM, distance=Distance.COSINE)
        },
        hnsw_config=HnswConfigDiff(m=16, ef_construct=100),
    )

    # Reindexa todos os itens publicados
    items = list(
        await session.scalars(
            select(Item)
            .join(Lesson, Lesson.id == Item.lesson_id)
            .join(Unit, Unit.id == Lesson.unit_id)
            .where(Unit.is_published.is_(True), Lesson.is_published.is_(True))
            .order_by(Item.order_index)
        )
    )

    for item in items:
        # Busca a unit do item via lesson_id
        unit = None
        if item.lesson_id:
            lesson = await session.get(Lesson, item.lesson_id)
            if lesson and lesson.unit_id:
                unit = await session.get(Unit, lesson.unit_id)

        payload = await _build_item_payload(session, item, unit.target_language if unit else "es")
        text_parts = [item.front_text]
        if item.example:
            text_parts.append(item.example)
        for k in ("gloss_pt_br", "gloss_en_us"):
            if payload.get(k):
                text_parts.append(payload[k])
        text = " ".join(text_parts)

        dense, _ = embed_hybrid([text])  # Use apenas dense
        point = PointStruct(
            id=str(item.id),
            vector={"dense": dense[0].tolist()},
            payload=payload,
        )
        await client.upsert(collection_name=new_collection, points=[point])

    # Reindexa decks
    decks = list(
        await session.scalars(select(Deck).where(Deck.is_official.is_(True)))
    )
    for deck in decks:
        await upsert_deck(session, deck)

    return len(items) + len(decks)