"""Modelos de identidade: usuário, sessão de autenticação e convite."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import JSON, CheckConstraint, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from ..db import Base
from .base import Timestamp, UUIDBinary, utcnow, uuid7


class User(Base):
    __tablename__ = "users"
    __table_args__ = (CheckConstraint("role IN ('owner','member')", name="ck_users_role"),)

    id: Mapped[uuid.UUID] = mapped_column(UUIDBinary, primary_key=True, default=uuid7)
    email: Mapped[str] = mapped_column(String(254), unique=True)
    name: Mapped[str] = mapped_column(String(120))
    password_hash: Mapped[str] = mapped_column(String(255))
    role: Mapped[str] = mapped_column(String(16), default="member")
    ui_language: Mapped[str] = mapped_column(String(10), default="pt-BR")
    settings: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    is_active: Mapped[bool] = mapped_column(default=True)
    last_login_at: Mapped[datetime | None] = mapped_column(Timestamp, nullable=True)
    created_at: Mapped[datetime] = mapped_column(Timestamp, default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(Timestamp, default=utcnow, onupdate=utcnow)


class AuthSession(Base):
    """Refresh token opaco. Guardamos só o hash — o valor cru nunca vai ao banco."""

    __tablename__ = "auth_sessions"

    id: Mapped[uuid.UUID] = mapped_column(UUIDBinary, primary_key=True, default=uuid7)
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUIDBinary, ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    token_hash: Mapped[str] = mapped_column(String(64), unique=True)
    expires_at: Mapped[datetime] = mapped_column(Timestamp)
    revoked_at: Mapped[datetime | None] = mapped_column(Timestamp, nullable=True)
    user_agent: Mapped[str | None] = mapped_column(String(255), nullable=True)
    ip: Mapped[str | None] = mapped_column(String(45), nullable=True)
    created_at: Mapped[datetime] = mapped_column(Timestamp, default=utcnow)


class Invite(Base):
    """Convite por e-mail. O token só é exibido uma vez, na criação."""

    __tablename__ = "invites"

    id: Mapped[uuid.UUID] = mapped_column(UUIDBinary, primary_key=True, default=uuid7)
    email: Mapped[str] = mapped_column(String(254), index=True)
    role: Mapped[str] = mapped_column(String(16), default="member")
    token_hash: Mapped[str] = mapped_column(String(64), unique=True)
    expires_at: Mapped[datetime] = mapped_column(Timestamp)
    accepted_at: Mapped[datetime | None] = mapped_column(Timestamp, nullable=True)
    accepted_by: Mapped[uuid.UUID | None] = mapped_column(
        UUIDBinary, ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    created_by: Mapped[uuid.UUID] = mapped_column(
        UUIDBinary, ForeignKey("users.id", ondelete="CASCADE")
    )
    created_at: Mapped[datetime] = mapped_column(Timestamp, default=utcnow)
