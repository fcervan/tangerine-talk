"""Cria conteúdo versionado: trilha, lições, itens, exercícios e baralhos.

Revision ID: 0004
Revises: 0003
Create Date: 2026-11-24
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import mysql

revision = "0004"
down_revision = "0003"
branch_labels = None
depends_on = None

_TABLE_OPTIONS = {"mysql_charset": "utf8mb4", "mysql_collate": "utf8mb4_0900_as_cs"}


def uuid_type() -> sa.types.TypeEngine[object]:
    return sa.LargeBinary(16).with_variant(mysql.BINARY(16), "mysql")


def timestamp_type() -> sa.types.TypeEngine[object]:
    return sa.DateTime().with_variant(mysql.DATETIME(fsp=6), "mysql")


def upgrade() -> None:
    op.create_table(
        "decks",
        sa.Column("id", uuid_type(), primary_key=True),
        sa.Column("target_language", sa.String(35), nullable=False),
        sa.Column("level", sa.String(2), nullable=False),
        sa.Column("slug", sa.String(80), nullable=False),
        sa.Column("title", sa.String(160), nullable=False),
        sa.Column("description", sa.String(500), nullable=True),
        sa.Column("is_official", sa.Boolean(), nullable=False),
        sa.Column("created_at", timestamp_type(), nullable=False),
        sa.Column("updated_at", timestamp_type(), nullable=False),
        sa.CheckConstraint("level IN ('A1','A2','B1','B2','C1','C2')", name="ck_decks_level"),
        sa.UniqueConstraint("target_language", "slug", name="uq_decks_target_slug"),
        **_TABLE_OPTIONS,
    )
    op.create_index("ix_decks_target_language", "decks", ["target_language"])

    op.create_table(
        "units",
        sa.Column("id", uuid_type(), primary_key=True),
        sa.Column("target_language", sa.String(35), nullable=False),
        sa.Column("level", sa.String(2), nullable=False),
        sa.Column("slug", sa.String(80), nullable=False),
        sa.Column("title", sa.String(160), nullable=False),
        sa.Column("description", sa.String(500), nullable=True),
        sa.Column("order_index", sa.Integer(), nullable=False),
        sa.Column(
            "prerequisite_id",
            uuid_type(),
            sa.ForeignKey("units.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("is_published", sa.Boolean(), nullable=False),
        sa.Column("created_at", timestamp_type(), nullable=False),
        sa.Column("updated_at", timestamp_type(), nullable=False),
        sa.CheckConstraint("level IN ('A1','A2','B1','B2','C1','C2')", name="ck_units_level"),
        sa.UniqueConstraint("target_language", "slug", name="uq_units_target_slug"),
        **_TABLE_OPTIONS,
    )
    op.create_index("ix_units_target_language", "units", ["target_language"])

    op.create_table(
        "lessons",
        sa.Column("id", uuid_type(), primary_key=True),
        sa.Column(
            "unit_id",
            uuid_type(),
            sa.ForeignKey("units.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("slug", sa.String(80), nullable=False),
        sa.Column("title", sa.String(160), nullable=False),
        sa.Column("order_index", sa.Integer(), nullable=False),
        sa.Column("kind", sa.String(16), nullable=False),
        sa.Column("xp_reward", sa.Integer(), nullable=False),
        sa.Column("is_published", sa.Boolean(), nullable=False),
        sa.Column("created_at", timestamp_type(), nullable=False),
        sa.Column("updated_at", timestamp_type(), nullable=False),
        sa.CheckConstraint("kind IN ('lesson','review')", name="ck_lessons_kind"),
        sa.UniqueConstraint("unit_id", "slug", name="uq_lessons_unit_slug"),
        **_TABLE_OPTIONS,
    )
    op.create_index("ix_lessons_unit_id", "lessons", ["unit_id"])

    op.create_table(
        "items",
        sa.Column("id", uuid_type(), primary_key=True),
        sa.Column(
            "lesson_id",
            uuid_type(),
            sa.ForeignKey("lessons.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("kind", sa.String(16), nullable=False),
        sa.Column("front_text", sa.String(255), nullable=False),
        sa.Column("example", sa.String(500), nullable=True),
        sa.Column("order_index", sa.Integer(), nullable=False),
        sa.Column("created_at", timestamp_type(), nullable=False),
        sa.CheckConstraint("kind IN ('word','phrase')", name="ck_items_kind"),
        **_TABLE_OPTIONS,
    )
    op.create_index("ix_items_lesson_id", "items", ["lesson_id"])

    op.create_table(
        "user_lesson_progress",
        sa.Column("id", uuid_type(), primary_key=True),
        sa.Column(
            "user_id",
            uuid_type(),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "lesson_id",
            uuid_type(),
            sa.ForeignKey("lessons.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("completed_at", timestamp_type(), nullable=False),
        sa.Column("score", sa.Integer(), nullable=True),
        sa.Column("created_at", timestamp_type(), nullable=False),
        sa.UniqueConstraint("user_id", "lesson_id", name="uq_progress_user_lesson"),
        **_TABLE_OPTIONS,
    )
    op.create_index(
        "ix_user_lesson_progress_user_id", "user_lesson_progress", ["user_id"]
    )
    op.create_index(
        "ix_user_lesson_progress_lesson_id", "user_lesson_progress", ["lesson_id"]
    )

    op.create_table(
        "deck_items",
        sa.Column(
            "deck_id",
            uuid_type(),
            sa.ForeignKey("decks.id", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.Column(
            "item_id",
            uuid_type(),
            sa.ForeignKey("items.id", ondelete="CASCADE"),
            primary_key=True,
        ),
        **_TABLE_OPTIONS,
    )

    op.create_table(
        "exercises",
        sa.Column("id", uuid_type(), primary_key=True),
        sa.Column(
            "lesson_id",
            uuid_type(),
            sa.ForeignKey("lessons.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "item_id",
            uuid_type(),
            sa.ForeignKey("items.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("type", sa.String(24), nullable=False),
        sa.Column("prompt", sa.String(500), nullable=False),
        sa.Column("answer", sa.String(500), nullable=False),
        sa.Column("options", sa.JSON(), nullable=True),
        sa.Column("order_index", sa.Integer(), nullable=False),
        sa.Column("created_at", timestamp_type(), nullable=False),
        sa.CheckConstraint(
            "type IN ('flashcard','multiple_choice','translation')",
            name="ck_exercises_type",
        ),
        **_TABLE_OPTIONS,
    )
    op.create_index("ix_exercises_lesson_id", "exercises", ["lesson_id"])

    op.create_table(
        "item_translations",
        sa.Column(
            "item_id",
            uuid_type(),
            sa.ForeignKey("items.id", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.Column("locale", sa.String(35), primary_key=True),
        sa.Column("gloss", sa.String(500), nullable=False),
        **_TABLE_OPTIONS,
    )


def downgrade() -> None:
    op.drop_table("item_translations")
    op.drop_index("ix_exercises_lesson_id", table_name="exercises")
    op.drop_table("exercises")
    op.drop_table("deck_items")
    op.drop_index("ix_user_lesson_progress_lesson_id", table_name="user_lesson_progress")
    op.drop_index("ix_user_lesson_progress_user_id", table_name="user_lesson_progress")
    op.drop_table("user_lesson_progress")
    op.drop_index("ix_items_lesson_id", table_name="items")
    op.drop_table("items")
    op.drop_index("ix_lessons_unit_id", table_name="lessons")
    op.drop_table("lessons")
    op.drop_index("ix_units_target_language", table_name="units")
    op.drop_table("units")
    op.drop_index("ix_decks_target_language", table_name="decks")
    op.drop_table("decks")
