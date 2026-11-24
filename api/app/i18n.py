"""Idioma da interface e idioma estudado: dois eixos independentes.

O locale da interface é aberto (qualquer BCP-47 simples); os dicionários
disponíveis ficam no front, que faz fallback para ``pt-BR``. O idioma alvo é
escolhido no onboarding e não depende da lista de locales da interface.
"""

from __future__ import annotations

import re
from typing import Literal

DEFAULT_LOCALE = "pt-BR"

# Locales com dicionário no front. Novos idiomas entram aqui e em
# lib/i18n/locales/ — nenhum código de domínio deve assumir só estes dois.
AVAILABLE_UI_LOCALES: tuple[str, ...] = ("pt-BR", "en-US")

# Aceita tanto a forma canônica quanto entradas como `en-us` e `zh-hans-cn`.
_LOCALE_RE = re.compile(
    r"^[a-zA-Z]{2,3}(?:-[a-zA-Z]{4,8})?(?:-[a-zA-Z]{2}|-[0-9]{3})?$"
)


def normalize_locale(value: str) -> str:
    """Valida e devolve o locale em forma canônica: ``pt-br`` → ``pt-BR``.

    Aceita ``pt-BR``, ``en-US``, ``ja-JP``, ``zh-Hans-CN`` e ``es-419``.
    Rejeita separadores inválidos e subcategorias desconhecidas.
    """

    parts = value.strip().split("-")
    if len(parts) > 3 or not _LOCALE_RE.fullmatch("-".join(parts)):
        raise ValueError("Código de idioma inválido. Use algo como pt-BR, en-US ou ja-JP.")

    parts[0] = parts[0].lower()
    for index, part in enumerate(parts[1:], start=1):
        if len(part) == 2:
            parts[index] = part.upper()
        elif part.isdigit():
            parts[index] = part
        else:
            parts[index] = part[:1].upper() + part[1:].lower()
    return "-".join(parts)


def base_language(locale: str) -> str:
    """Primeira subtag BCP-47, em minúsculas (``pt-BR`` → ``pt``)."""

    return locale.split("-", 1)[0].lower()


def exercise_mode(
    ui_language: str, target_language: str
) -> Literal["monolingual", "bilingual"]:
    """Mesma base dos dois lados significa deck monolingual, sem tradução."""

    if base_language(ui_language) == base_language(target_language):
        return "monolingual"
    return "bilingual"
