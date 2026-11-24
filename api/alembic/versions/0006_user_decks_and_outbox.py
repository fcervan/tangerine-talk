"""adiciona user_id em decks (baralhos próprios) + tabela content_outbox (sync Qdrant)

Revision ID: 0006_user_decks_and_outbox
Revises: 0005
Create Date: 2026-11-24
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = "0006"
down_revision = "0005"
branch_labels = None
depends_on = None


def uuid_type() -> sa.types.TypeEngine[object]:
    return sa.LargeBinary(16).with_variant(mysql.BINARY(16), "mysql")


def timestamp_type() -> sa.types.TypeEngine[object]:
    return sa.DateTime().with_variant(mysql.DATETIME(fsp=6), "mysql")


_TABLE_OPTIONS = {"mysql_charset": "utf8mb4", "mysql_collate": "utf8mb4_0900_as_cs"}


def upgrade() -> None:
    # 1. Adiciona user_id em decks (para baralhos próprios) - já pode existir
    from alembic import op
    import sqlalchemy as sa

    conn = op.get_bind()
    inspector = sa.inspect(conn)
    columns = [col["name"] for col in inspector.get_columns("decks")]

    if "user_id" not in columns:
        op.add_column(
            "decks",
            sa.Column(
                "user_id",
                uuid_type(),
                sa.ForeignKey("users.id", ondelete="CASCADE"),
                nullable=True,
            ),
        )
        op.create_index("ix_decks_user_id", "decks", ["user_id"])

    op.create_unique_constraint(
        "uq_decks_user_slug", "decks", ["user_id", "slug"]
    )

    # 2. Cria tabela content_outbox (sync MySQL → Qdrant)
    op.create_table(
        "content_outbox",
        sa.Column("id", uuid_type(), nullable=False),
        sa.Column(
            "event_type",
            sa.Enum(
                "item_upsert",
                "item_delete",
                "deck_upsert",
                "deck_delete",
                name="outbox_event_type",
            ),
            nullable=False,
            index=True,
        ),
        sa.Column("entity_id", uuid_type(), nullable=False, index=True),
        sa.Column("target_language", sa.String(length=35), nullable=False, index=True),
        sa.Column("payload", sa.JSON(), nullable=False),
        sa.Column("created_at", timestamp_type(), nullable=False),
        sa.Column("processed_at", timestamp_type(), nullable=True, index=True),
        sa.Column("attempts", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("last_error", sa.String(length=500), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        **_TABLE_OPTIONS,
    )
    op.create_index("ix_content_outbox_processed", "content_outbox", ["processed_at"])


def downgrade() -> None:
    op.drop_index("ix_content_outbox_processed", table_name="content_outbox")
    op.drop_table("content_outbox")
    op.drop_constraint("uq_decks_user_slug", "decks", type_="unique")
    op.drop_index("ix_decks_user_id", table_name="decks")
    op.drop_column("decks", "user_id")