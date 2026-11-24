"""Qdrant: índice vetorial derivado do MySQL (Fase 6).

MySQL é a fonte da verdade; Qdrant é reconstruível via outbox + worker.
"""

from __future__ import annotations

from .client import get_qdrant_client
from .embed import get_embedder
from .sync import (
    ensure_collection,
    reindex_all,
    sync_outbox,
)

__all__ = [
    "ensure_collection",
    "get_embedder",
    "get_qdrant_client",
    "reindex_all",
    "sync_outbox",
]