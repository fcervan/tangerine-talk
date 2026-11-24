"""Adiciona credenciais de provedores por usuário (BYOK).

Revision ID: 0003
Revises: 0002
Create Date: 2026-11-24
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import mysql

revision = "0003"
down_revision = "0002"
branch_labels = None
depends_on = None


def uuid_type() -> sa.types.TypeEngine[object]:
    return sa.LargeBinary(16).with_variant(mysql.BINARY(16), "mysql")


def timestamp_type() -> sa.types.TypeEngine[object]:
    return sa.DateTime().with_variant(mysql.DATETIME(fsp=6), "mysql")


def upgrade() -> None:
    op.create_table(
        "provider_credentials",
        sa.Column("id", uuid_type(), primary_key=True),
        sa.Column(
            "user_id",
            uuid_type(),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("provider", sa.String(32), nullable=False),
        sa.Column("api_key_encrypted", sa.Text(), nullable=True),
        sa.Column("key_hint", sa.String(32), nullable=True),
        sa.Column("base_url", sa.String(255), nullable=False),
        sa.Column("model", sa.String(120), nullable=False),
        sa.Column(
            "is_active", sa.Boolean(), nullable=False, server_default=sa.true()
        ),
        sa.Column("last_tested_at", timestamp_type(), nullable=True),
        sa.Column("last_used_at", timestamp_type(), nullable=True),
        sa.Column("last_error", sa.String(255), nullable=True),
        sa.Column("created_at", timestamp_type(), nullable=False),
        sa.Column("updated_at", timestamp_type(), nullable=False),
        sa.CheckConstraint(
            "provider IN ('groq','ollama_cloud','openrouter','ollama')",
            name="ck_provider_credentials_provider",
        ),
        sa.UniqueConstraint(
            "user_id", "provider", name="uq_provider_credentials_user_provider"
        ),
        mysql_charset="utf8mb4",
        mysql_collate="utf8mb4_0900_as_cs",
    )
    op.create_index("ix_provider_credentials_user_id", "provider_credentials", ["user_id"])


def downgrade() -> None:
    op.drop_index("ix_provider_credentials_user_id", table_name="provider_credentials")
    op.drop_table("provider_credentials")
