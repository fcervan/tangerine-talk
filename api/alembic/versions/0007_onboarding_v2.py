"""adiciona campos de onboarding v2 (idiomas de estudo, faixa de nível, programa)

Revision ID: 0007
Revises: 0006
Create Date: 2026-11-25
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

revision = "0007"
down_revision = "0006"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("users", sa.Column("study_languages", sa.JSON(), nullable=True))
    op.add_column("users", sa.Column("level_band", sa.String(length=16), nullable=True))
    op.add_column("users", sa.Column("program_source", sa.String(length=16), nullable=True))
    op.add_column("users", sa.Column("program_topics", sa.JSON(), nullable=True))


def downgrade() -> None:
    op.drop_column("users", "program_topics")
    op.drop_column("users", "program_source")
    op.drop_column("users", "level_band")
    op.drop_column("users", "study_languages")