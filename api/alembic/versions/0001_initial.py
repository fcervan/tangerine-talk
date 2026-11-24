"""Cria usuários, sessões de autenticação e convites.

Revision ID: 0001
Revises:
Create Date: 2026-11-24
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import mysql

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def uuid_type() -> sa.types.TypeEngine[object]:
    return sa.LargeBinary(16).with_variant(mysql.BINARY(16), "mysql")


def timestamp_type() -> sa.types.TypeEngine[object]:
    return sa.DateTime().with_variant(mysql.DATETIME(fsp=6), "mysql")


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", uuid_type(), primary_key=True),
        sa.Column("email", sa.String(254), nullable=False),
        sa.Column("name", sa.String(120), nullable=False),
        sa.Column("password_hash", sa.String(255), nullable=False),
        sa.Column("role", sa.String(16), nullable=False),
        sa.Column("ui_language", sa.String(10), nullable=False),
        sa.Column("settings", sa.JSON(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("last_login_at", timestamp_type(), nullable=True),
        sa.Column("created_at", timestamp_type(), nullable=False),
        sa.Column("updated_at", timestamp_type(), nullable=False),
        sa.CheckConstraint("role IN ('owner','member')", name="ck_users_role"),
        mysql_charset="utf8mb4",
        mysql_collate="utf8mb4_0900_as_cs",
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)

    op.create_table(
        "auth_sessions",
        sa.Column("id", uuid_type(), primary_key=True),
        sa.Column(
            "user_id",
            uuid_type(),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("token_hash", sa.String(64), nullable=False),
        sa.Column("expires_at", timestamp_type(), nullable=False),
        sa.Column("revoked_at", timestamp_type(), nullable=True),
        sa.Column("user_agent", sa.String(255), nullable=True),
        sa.Column("ip", sa.String(45), nullable=True),
        sa.Column("created_at", timestamp_type(), nullable=False),
        sa.UniqueConstraint("token_hash", name="uq_auth_sessions_token_hash"),
        mysql_charset="utf8mb4",
        mysql_collate="utf8mb4_0900_as_cs",
    )
    op.create_index("ix_auth_sessions_user_id", "auth_sessions", ["user_id"])

    op.create_table(
        "invites",
        sa.Column("id", uuid_type(), primary_key=True),
        sa.Column("email", sa.String(254), nullable=False),
        sa.Column("role", sa.String(16), nullable=False),
        sa.Column("token_hash", sa.String(64), nullable=False),
        sa.Column("expires_at", timestamp_type(), nullable=False),
        sa.Column("accepted_at", timestamp_type(), nullable=True),
        sa.Column(
            "accepted_by",
            uuid_type(),
            sa.ForeignKey("users.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column(
            "created_by",
            uuid_type(),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("created_at", timestamp_type(), nullable=False),
        sa.UniqueConstraint("token_hash", name="uq_invites_token_hash"),
        mysql_charset="utf8mb4",
        mysql_collate="utf8mb4_0900_as_cs",
    )
    op.create_index("ix_invites_email", "invites", ["email"])


def downgrade() -> None:
    op.drop_table("invites")
    op.drop_table("auth_sessions")
    op.drop_table("users")
