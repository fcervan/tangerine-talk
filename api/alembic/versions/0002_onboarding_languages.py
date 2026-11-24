"""Adiciona idioma alvo e estado do onboarding aos usuários.

Revision ID: 0002
Revises: 0001
Create Date: 2026-11-24
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "0002"
down_revision = "0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table("users") as batch_op:
        batch_op.alter_column(
            "ui_language",
            existing_type=sa.String(10),
            type_=sa.String(35),
            existing_nullable=False,
            nullable=False,
        )
        batch_op.add_column(sa.Column("target_language", sa.String(35), nullable=True))
        batch_op.add_column(
            sa.Column(
                "onboarding_completed",
                sa.Boolean(),
                nullable=False,
                server_default=sa.false(),
            )
        )


def downgrade() -> None:
    with op.batch_alter_table("users") as batch_op:
        batch_op.drop_column("onboarding_completed")
        batch_op.drop_column("target_language")
        batch_op.alter_column(
            "ui_language",
            existing_type=sa.String(35),
            type_=sa.String(10),
            existing_nullable=False,
            nullable=False,
        )
