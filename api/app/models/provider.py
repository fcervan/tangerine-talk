"""Credencial de provedor de IA por usuário (BYOK)."""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import CheckConstraint, ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from ..db import Base
from .base import Timestamp, UUIDBinary, utcnow, uuid7


class ProviderCredential(Base):
    """Chave do próprio usuário, cifrada em repouso.

    A coluna `api_key_encrypted` nunca sai da API. `key_hint` é só uma dica
    visual (`sk-…a1b2`) para a pessoa reconhecer a chave cadastrada.
    """

    __tablename__ = "provider_credentials"
    __table_args__ = (
        CheckConstraint(
            "provider IN ('groq','ollama_cloud','openrouter','ollama')",
            name="ck_provider_credentials_provider",
        ),
        UniqueConstraint("user_id", "provider", name="uq_provider_credentials_user_provider"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUIDBinary, primary_key=True, default=uuid7)
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUIDBinary, ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    provider: Mapped[str] = mapped_column(String(32))
    api_key_encrypted: Mapped[str | None] = mapped_column(Text, nullable=True)
    key_hint: Mapped[str | None] = mapped_column(String(32), nullable=True)
    base_url: Mapped[str] = mapped_column(String(255))
    model: Mapped[str] = mapped_column(String(120))
    is_active: Mapped[bool] = mapped_column(default=True)
    last_tested_at: Mapped[datetime | None] = mapped_column(Timestamp, nullable=True)
    last_used_at: Mapped[datetime | None] = mapped_column(Timestamp, nullable=True)
    last_error: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(Timestamp, default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(Timestamp, default=utcnow, onupdate=utcnow)
