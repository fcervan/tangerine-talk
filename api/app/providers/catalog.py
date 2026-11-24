"""Catálogo estático de provedores e roteamento por tarefa.

Capacidades e ordem de fallback são decisão do produto: nunca vêm do cliente.
O catálogo é a única lista de slugs aceitos pela API.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

ProviderSlug = Literal["groq", "ollama_cloud", "openrouter", "ollama"]
Capability = Literal["chat", "stream", "structured", "vision", "embeddings", "tts", "stt"]
TaskName = Literal["chat", "feedback", "correction", "embedding", "tts", "stt"]


@dataclass(frozen=True, slots=True)
class ProviderSpec:
    slug: str
    label: str
    default_base_url: str
    default_model: str
    capabilities: frozenset[Capability]
    needs_key: bool
    cloud: bool
    fallback_order: int
    key_url: str


PROVIDERS: dict[str, ProviderSpec] = {
    "groq": ProviderSpec(
        slug="groq",
        label="Groq",
        default_base_url="https://api.groq.com/openai/v1",
        default_model="llama-3.3-70b-versatile",
        capabilities=frozenset({"chat", "stream", "structured", "stt"}),
        needs_key=True,
        cloud=True,
        fallback_order=0,
        key_url="https://console.groq.com/keys",
    ),
    "ollama_cloud": ProviderSpec(
        slug="ollama_cloud",
        label="Ollama Cloud",
        default_base_url="https://ollama.com/v1",
        default_model="gpt-oss:120b",
        capabilities=frozenset({"chat", "stream", "structured", "tts", "stt"}),
        needs_key=True,
        cloud=True,
        fallback_order=1,
        key_url="https://ollama.com/settings/keys",
    ),
    "openrouter": ProviderSpec(
        slug="openrouter",
        label="OpenRouter",
        default_base_url="https://openrouter.ai/api/v1",
        default_model="openai/gpt-4o-mini",
        capabilities=frozenset({"chat", "stream", "structured", "embeddings", "tts", "stt"}),
        needs_key=True,
        cloud=True,
        fallback_order=2,
        key_url="https://openrouter.ai/keys",
    ),
    "ollama": ProviderSpec(
        slug="ollama",
        label="Ollama (local)",
        default_base_url="http://127.0.0.1:11434/v1",
        default_model="llama3.2",
        capabilities=frozenset({"chat", "stream", "embeddings"}),
        needs_key=False,
        cloud=False,
        fallback_order=99,
        key_url="",
    ),
}

FALLBACK_ORDER: tuple[str, ...] = ("groq", "ollama_cloud", "openrouter", "ollama")

TASK_CAPABILITIES: dict[TaskName, frozenset[Capability]] = {
    "chat": frozenset({"chat"}),
    "feedback": frozenset({"chat"}),
    "correction": frozenset({"structured"}),
    "embedding": frozenset({"embeddings"}),
    "tts": frozenset({"tts"}),
    "stt": frozenset({"stt"}),
}


def get_spec(slug: str) -> ProviderSpec | None:
    return PROVIDERS.get(slug)


def public_catalog() -> list[dict[str, object]]:
    """Metadados seguros para a UI. Não inclui chave nem segredo."""
    return [
        {
            "slug": spec.slug,
            "label": spec.label,
            "capabilities": sorted(spec.capabilities),
            "needs_key": spec.needs_key,
            "cloud": spec.cloud,
            "default_model": spec.default_model,
            "key_url": spec.key_url,
        }
        for spec in sorted(PROVIDERS.values(), key=lambda item: item.fallback_order)
    ]
