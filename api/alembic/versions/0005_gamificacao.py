"""adiciona gamificação: XP, streak, SRS, selos, ligas, missões

Revision ID: 0005
Revises: 0004
Create Date: 2026-11-24
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql


def uuid_type() -> sa.types.TypeEngine[object]:
    return sa.LargeBinary(16).with_variant(mysql.BINARY(16), "mysql")


def timestamp_type() -> sa.types.TypeEngine[object]:
    return sa.DateTime().with_variant(mysql.DATETIME(fsp=6), "mysql")


# revision identifiers, used by Alembic.
revision = "0005"
down_revision = "0004"
branch_labels = None
depends_on = None

_TABLE_OPTIONS = {"mysql_charset": "utf8mb4", "mysql_collate": "utf8mb4_0900_as_cs"}


def upgrade() -> None:
    # user_gamification
    op.create_table(
        "user_gamification",
        sa.Column("id", uuid_type(), nullable=False),
        sa.Column("user_id", uuid_type(), nullable=False),
        sa.Column("xp", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("level", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("current_streak", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("longest_streak", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("last_streak_date", sa.Date(), nullable=True),
        sa.Column("streak_frozen", sa.Boolean(), nullable=False, server_default="0"),
        sa.Column("daily_goal_minutes", sa.Integer(), nullable=False, server_default="15"),
        sa.Column("minutes_today", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("last_minutes_date", sa.Date(), nullable=True),
        sa.Column("league_tier", sa.String(length=16), nullable=False, server_default="bronze"),
        sa.Column("league_xp_this_week", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("league_rank", sa.Integer(), nullable=True),
        sa.Column("league_week_start", sa.Date(), nullable=True),
        sa.Column("total_lessons_completed", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("total_conversations", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("total_flashcards_reviewed", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", timestamp_type(), nullable=False),
        sa.Column("updated_at", timestamp_type(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", name="uq_gamification_user"),
        **_TABLE_OPTIONS,
    )
    op.create_index("ix_gamification_xp", "user_gamification", ["xp"])

    # user_streak_days
    op.create_table(
        "user_streak_days",
        sa.Column("id", uuid_type(), nullable=False),
        sa.Column("user_id", uuid_type(), nullable=False),
        sa.Column("day", sa.Date(), nullable=False),
        sa.Column("minutes", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("lessons_completed", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", timestamp_type(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "day", name="uq_streak_user_day"),
        **_TABLE_OPTIONS,
    )
    op.create_index("ix_streak_user_day", "user_streak_days", ["user_id", "day"])

    # user_badges
    op.create_table(
        "user_badges",
        sa.Column("id", uuid_type(), nullable=False),
        sa.Column("user_id", uuid_type(), nullable=False),
        sa.Column("slug", sa.String(length=64), nullable=False),
        sa.Column("earned_at", timestamp_type(), nullable=False),
        sa.Column("meta", sa.JSON(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "slug", name="uq_badge_user_slug"),
        **_TABLE_OPTIONS,
    )
    op.create_index("ix_badge_user_slug", "user_badges", ["user_id", "slug"])

    # user_srs_items
    op.create_table(
        "user_srs_items",
        sa.Column("id", uuid_type(), nullable=False),
        sa.Column("user_id", uuid_type(), nullable=False),
        sa.Column("item_id", uuid_type(), nullable=False),
        sa.Column("interval_days", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("ease_factor", sa.Float(), nullable=False, server_default="2.5"),
        sa.Column("repetitions", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("due_date", sa.Date(), nullable=False),
        sa.Column("last_quality", sa.Integer(), nullable=True),
        sa.Column("last_reviewed_at", timestamp_type(), nullable=True),
        sa.Column("created_at", timestamp_type(), nullable=False),
        sa.Column("updated_at", timestamp_type(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["item_id"], ["items.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "item_id", name="uq_srs_user_item"),
        **_TABLE_OPTIONS,
    )
    op.create_index("ix_srs_user_due", "user_srs_items", ["user_id", "due_date"])

    # user_league_weeks
    op.create_table(
        "user_league_weeks",
        sa.Column("id", uuid_type(), nullable=False),
        sa.Column("user_id", uuid_type(), nullable=False),
        sa.Column("week_start", sa.Date(), nullable=False),
        sa.Column("tier", sa.String(length=16), nullable=False),
        sa.Column("xp", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("rank", sa.Integer(), nullable=True),
        sa.Column("promoted", sa.Boolean(), nullable=False, server_default="0"),
        sa.Column("demoted", sa.Boolean(), nullable=False, server_default="0"),
        sa.Column("created_at", timestamp_type(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "week_start", name="uq_league_user_week"),
        **_TABLE_OPTIONS,
    )
    op.create_index("ix_league_week_tier_rank", "user_league_weeks", ["week_start", "tier", "rank"])

    # user_missions
    op.create_table(
        "user_missions",
        sa.Column("id", uuid_type(), nullable=False),
        sa.Column("user_id", uuid_type(), nullable=False),
        sa.Column("day", sa.Date(), nullable=False),
        sa.Column("type", sa.String(length=32), nullable=False),
        sa.Column("target", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("progress", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("completed", sa.Boolean(), nullable=False, server_default="0"),
        sa.Column("xp_reward", sa.Integer(), nullable=False, server_default="5"),
        sa.Column("created_at", timestamp_type(), nullable=False),
        sa.Column("updated_at", timestamp_type(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "day", "type", name="uq_mission_user_day_type"),
        **_TABLE_OPTIONS,
    )
    op.create_index("ix_mission_user_day", "user_missions", ["user_id", "day"])


def downgrade() -> None:
    op.drop_index("ix_mission_user_day", table_name="user_missions")
    op.drop_table("user_missions")
    op.drop_index("ix_league_week_tier_rank", table_name="user_league_weeks")
    op.drop_table("user_league_weeks")
    op.drop_index("ix_srs_user_due", table_name="user_srs_items")
    op.drop_table("user_srs_items")
    op.drop_index("ix_badge_user_slug", table_name="user_badges")
    op.drop_table("user_badges")
    op.drop_index("ix_streak_user_day", table_name="user_streak_days")
    op.drop_table("user_streak_days")
    op.drop_index("ix_gamification_xp", table_name="user_gamification")
    op.drop_table("user_gamification")