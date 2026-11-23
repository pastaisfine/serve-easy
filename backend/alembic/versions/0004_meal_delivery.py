"""Add integrated meal providers, orders and location delivery batches.

Revision ID: 0004
Revises: 0003
Create Date: 2026-11-18

The four legacy cafeteria accounts are archived and their menus deactivated.
Food orders and line items are left untouched.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = "0004"
down_revision: Union[str, Sequence[str], None] = "0003"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column("is_active", sa.Boolean(), server_default=sa.true(), nullable=False),
    )

    op.create_table(
        "food_providers",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("name", sa.String(length=120), nullable=False, unique=True),
        sa.Column("image", sa.String(length=500), nullable=True),
        sa.Column("is_active", sa.Boolean(), server_default=sa.true(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_table(
        "food_provider_staff",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("provider_id", sa.String(length=36), nullable=False),
        sa.Column("user_id", sa.String(length=36), nullable=False),
        sa.ForeignKeyConstraint(["provider_id"], ["food_providers.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("provider_id", "user_id", name="uq_food_provider_staff_provider_user"),
    )
    op.create_index("ix_food_provider_staff_provider_id", "food_provider_staff", ["provider_id"])
    op.create_index("ix_food_provider_staff_user_id", "food_provider_staff", ["user_id"])

    op.add_column("food_items", sa.Column("provider_id", sa.String(length=36), nullable=True))
    op.add_column(
        "food_items",
        sa.Column("is_demo", sa.Boolean(), server_default=sa.false(), nullable=False),
    )
    op.alter_column("food_items", "seller_id", existing_type=sa.String(length=36), nullable=True)
    op.create_foreign_key(
        "fk_food_items_provider_id_food_providers",
        "food_items",
        "food_providers",
        ["provider_id"],
        ["id"],
        ondelete="CASCADE",
    )
    op.create_index("ix_food_items_provider_id", "food_items", ["provider_id"])

    op.execute(
        "UPDATE users SET is_active = false "
        "WHERE role = 'food_seller' "
        "AND name IN ('Kak Min', 'Mak Siti', 'Pak Lah', 'Western Corner KTR')"
    )
    op.execute(
        "UPDATE food_items SET available = false "
        "WHERE seller_id IN ("
        "SELECT id FROM users WHERE role = 'food_seller' AND is_active = false"
        ")"
    )

    op.create_table(
        "food_delivery_batches",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("provider_id", sa.String(length=36), nullable=False),
        sa.Column(
            "meal_session",
            postgresql.ENUM("lunch", "dinner", name="meal_session", create_type=False),
            nullable=False,
        ),
        sa.Column("delivery_date", sa.Date(), nullable=False),
        sa.Column("pickup_location", sa.String(length=120), nullable=False),
        sa.Column(
            "status",
            sa.Enum("preparing", "on_the_way", "delivered", name="delivery_status"),
            server_default="preparing",
            nullable=False,
        ),
        sa.Column("proof_image", sa.String(length=500), nullable=True),
        sa.Column("delivered_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["provider_id"], ["food_providers.id"], ondelete="CASCADE"),
        sa.UniqueConstraint(
            "provider_id",
            "meal_session",
            "delivery_date",
            "pickup_location",
            name="uq_food_delivery_batch_scope",
        ),
    )
    op.create_index(
        "ix_food_delivery_batches_provider_id",
        "food_delivery_batches",
        ["provider_id"],
    )
    op.create_index(
        "ix_food_delivery_batches_delivery_date",
        "food_delivery_batches",
        ["delivery_date"],
    )

    op.add_column(
        "order_line_items",
        sa.Column("item_name", sa.String(length=150), nullable=True),
    )
    op.execute(
        "UPDATE order_line_items SET item_name = food_items.name "
        "FROM food_items WHERE order_line_items.item_id = food_items.id"
    )

    op.add_column("food_orders", sa.Column("provider_id", sa.String(length=36), nullable=True))
    op.add_column(
        "food_orders", sa.Column("delivery_batch_id", sa.String(length=36), nullable=True)
    )
    op.alter_column("food_orders", "seller_id", existing_type=sa.String(length=36), nullable=True)
    op.create_foreign_key(
        "fk_food_orders_provider_id_food_providers",
        "food_orders",
        "food_providers",
        ["provider_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_foreign_key(
        "fk_food_orders_delivery_batch_id_food_delivery_batches",
        "food_orders",
        "food_delivery_batches",
        ["delivery_batch_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_index("ix_food_orders_provider_id", "food_orders", ["provider_id"])
    op.create_index("ix_food_orders_delivery_batch_id", "food_orders", ["delivery_batch_id"])


def downgrade() -> None:
    op.drop_index("ix_food_orders_delivery_batch_id", table_name="food_orders")
    op.drop_index("ix_food_orders_provider_id", table_name="food_orders")
    op.drop_constraint(
        "fk_food_orders_delivery_batch_id_food_delivery_batches", "food_orders", type_="foreignkey"
    )
    op.drop_constraint(
        "fk_food_orders_provider_id_food_providers", "food_orders", type_="foreignkey"
    )
    op.drop_column("food_orders", "delivery_batch_id")
    op.drop_column("food_orders", "provider_id")
    op.alter_column("food_orders", "seller_id", existing_type=sa.String(length=36), nullable=False)
    op.drop_column("order_line_items", "item_name")

    op.drop_index("ix_food_delivery_batches_delivery_date", table_name="food_delivery_batches")
    op.drop_index("ix_food_delivery_batches_provider_id", table_name="food_delivery_batches")
    op.drop_table("food_delivery_batches")
    sa.Enum(name="delivery_status").drop(op.get_bind(), checkfirst=True)

    op.drop_index("ix_food_items_provider_id", table_name="food_items")
    op.drop_constraint("fk_food_items_provider_id_food_providers", "food_items", type_="foreignkey")
    op.drop_column("food_items", "is_demo")
    op.drop_column("food_items", "provider_id")
    op.alter_column("food_items", "seller_id", existing_type=sa.String(length=36), nullable=False)

    op.drop_index("ix_food_provider_staff_user_id", table_name="food_provider_staff")
    op.drop_index("ix_food_provider_staff_provider_id", table_name="food_provider_staff")
    op.drop_table("food_provider_staff")
    op.drop_table("food_providers")
    op.drop_column("users", "is_active")
