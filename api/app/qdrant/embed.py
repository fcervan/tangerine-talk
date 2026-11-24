"""Embedder para vetorização de conteúdo (Fase 6).

Usa sentence-transformers (BGE-M3 recomendado) para embeddings denso + esparso.
O modelo é carregado uma vez e reutilizado (singleton).
"""

from __future__ import annotations

from functools import lru_cache
from typing import Any

import numpy as np
import torch
from sentence_transformers import SentenceTransformer

# Modelo recomendado: BGE-M3 (multilíngue, denso + esparso, 1024 dims)
# Alternativa leve: BAAI/bge-small-en-v1.5 (384 dims)
DEFAULT_MODEL = "BAAI/bge-m3"


@lru_cache(maxsize=1)
def _load_model(model_name: str = DEFAULT_MODEL) -> SentenceTransformer:
    """Carrega o modelo de embedding (com cache)."""
    device = "cuda" if torch.cuda.is_available() else "cpu"
    return SentenceTransformer(model_name, device=device)


def get_embedder(model_name: str = DEFAULT_MODEL) -> SentenceTransformer:
    """Retorna o embedder singleton."""
    return _load_model(model_name)


def embed_texts(texts: list[str], model_name: str = DEFAULT_MODEL) -> np.ndarray:
    """Gera embeddings para uma lista de textos (denso)."""
    embedder = get_embedder(model_name)
    embeddings = embedder.encode(
        texts,
        batch_size=32,
        show_progress_bar=False,
        convert_to_numpy=True,
        normalize_embeddings=True,  # cosine distance
    )
    return embeddings.astype(np.float32)


def embed_sparse(texts: list[str], model_name: str = DEFAULT_MODEL) -> list[dict[str, Any]]:
    """Gera embeddings esparsos (BM25-style) para busca híbrida.

    Requer modelo com suporte a sparse (ex.: BGE-M3).
    Retorna lista de dicts {indices: [...], values: [...]} compatível com Qdrant.
    """
    embedder = get_embedder(model_name)
    if not hasattr(embedder, "encode_sparse"):
        raise NotImplementedError(
            f"Modelo {model_name} não suporta embeddings esparsos."
        )
    # mypy acha que encode_sparse é um Tensor - usar cast para contornar
    from typing import cast
    encode_sparse = cast(Any, embedder.encode_sparse)
    sparse = encode_sparse(
        texts,
        batch_size=32,
        show_progress_bar=False,
    )
    result: list[dict[str, Any]] = []
    for s in sparse:
        indices = s.indices.tolist() if hasattr(s.indices, "tolist") else list(s.indices)
        values = s.values.tolist() if hasattr(s.values, "tolist") else list(s.values)
        result.append({"indices": indices, "values": values})
    return result


def embed_hybrid(
    texts: list[str], model_name: str = DEFAULT_MODEL
) -> tuple[np.ndarray, list[dict[str, Any]]]:
    """Gera embeddings denso + esparso para busca híbrida no Qdrant."""
    dense = embed_texts(texts, model_name)
    sparse = embed_sparse(texts, model_name)
    return dense, sparse