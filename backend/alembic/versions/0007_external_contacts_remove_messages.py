"""Add external contact details and remove in-app messages.

Revision ID: 0007
Revises: 0006
Create Date: 2026-11-23
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0007"
down_revision: Union[str, Sequence[str], None] = "0006"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("users", sa.Column("telegram_username", sa.String(length=32), nullable=True))
    op.add_column("food_providers", sa.Column("whatsapp", sa.String(length=32), nullable=True))
    op.add_column(
        "food_providers", sa.Column("telegram_username", sa.String(length=32), nullable=True)
    )
    op.drop_index("ix_messages_conversation", table_name="messages")
    op.drop_index("ix_messages_receiver_id", table_name="messages")
    op.drop_table("messages")


def downgrade() -> None:
    op.create_table(
        "messages",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("sender_id", sa.String(length=36), nullable=False),
        sa.Column("receiver_id", sa.String(length=36), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.CheckConstraint("sender_id <> receiver_id", name="ck_messages_not_self"),
        sa.ForeignKeyConstraint(["receiver_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["sender_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_messages_conversation",
        "messages",
        ["sender_id", "receiver_id", "created_at"],
    )
    op.create_index("ix_messages_receiver_id", "messages", ["receiver_id"])
    op.drop_column("food_providers", "telegram_username")
    op.drop_column("food_providers", "whatsapp")
    op.drop_column("users", "telegram_username")
