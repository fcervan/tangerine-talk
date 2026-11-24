"""Cliente Qdrant assíncrono com configuração centralizada."""

from __future__ import annotations

from qdrant_client import AsyncQdrantClient

from ..config import settings

_client: AsyncQdrantClient | None = None


def get_qdrant_client() -> AsyncQdrantClient:
    """Retorna o cliente Qdrant singleton (lazy init)."""
    global _client
    if _client is None:
        _client = AsyncQdrantClient(
            url=settings.qdrant_url,
            api_key=settings.qdrant_api_key or None,
            timeout=int(settings.qdrant_timeout),
        )
    return _client


async def close_qdrant_client() -> None:
    """Fecha o cliente Qdrant (para shutdown da aplicação)."""
    global _client
    if _client is not None:
        await _client.close()
        _client = None