"""adiciona a escolha de provedor de inferência feita no onboarding

Revision ID: 0008
Revises: 0007
Create Date: 2026-11-26
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

revision = "0008"
down_revision = "0007"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "users", sa.Column("inference_provider", sa.String(length=32), nullable=True)
    )
    op.add_column("users", sa.Column("inference_fallbacks", sa.JSON(), nullable=True))


def downgrade() -> None:
    op.drop_column("users", "inference_fallbacks")
    op.drop_column("users", "inference_provider")
