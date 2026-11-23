"""Add product purchase requests and default service booking status.

Revision ID: 0005
Revises: 0004
Create Date: 2026-11-23
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = "0005"
down_revision: Union[str, Sequence[str], None] = "0004"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("ALTER TYPE listing_status ADD VALUE IF NOT EXISTS 'reserved' BEFORE 'sold'")
    op.alter_column(
        "service_bookings",
        "status",
        existing_type=postgresql.ENUM(
            "pending", "accepted", "declined", "completed", "cancelled", name="booking_status"
        ),
        server_default="pending",
    )

    product_order_status = postgresql.ENUM(
        "pending",
        "accepted",
        "declined",
        "completed",
        "cancelled",
        name="product_order_status",
    )
    product_order_status.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "product_orders",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("listing_id", sa.String(length=36), nullable=False),
        sa.Column("buyer_id", sa.String(length=36), nullable=False),
        sa.Column("seller_id", sa.String(length=36), nullable=False),
        sa.Column("listing_title", sa.String(length=200), nullable=False),
        sa.Column("listing_image", sa.String(length=500), nullable=True),
        sa.Column("price", sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column("meetup_spot", sa.String(length=200), nullable=False),
        sa.Column("buyer_note", sa.Text(), nullable=True),
        sa.Column(
            "status",
            postgresql.ENUM(
                "pending",
                "accepted",
                "declined",
                "completed",
                "cancelled",
                name="product_order_status",
                create_type=False,
            ),
            server_default="pending",
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.CheckConstraint("buyer_id <> seller_id", name="ck_product_orders_no_self_purchase"),
        sa.ForeignKeyConstraint(["buyer_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["seller_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["listing_id"], ["product_listings.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_product_orders_listing_id", "product_orders", ["listing_id"])
    op.create_index("ix_product_orders_buyer_id", "product_orders", ["buyer_id"])
    op.create_index("ix_product_orders_seller_id", "product_orders", ["seller_id"])
    op.create_index(
        "uq_product_orders_active_listing",
        "product_orders",
        ["listing_id"],
        unique=True,
        postgresql_where=sa.text("status IN ('pending', 'accepted')"),
    )


def downgrade() -> None:
    op.drop_index("uq_product_orders_active_listing", table_name="product_orders")
    op.drop_index("ix_product_orders_seller_id", table_name="product_orders")
    op.drop_index("ix_product_orders_buyer_id", table_name="product_orders")
    op.drop_index("ix_product_orders_listing_id", table_name="product_orders")
    op.drop_table("product_orders")
    postgresql.ENUM(name="product_order_status").drop(op.get_bind(), checkfirst=True)

    op.alter_column(
        "service_bookings",
        "status",
        existing_type=postgresql.ENUM(
            "pending", "accepted", "declined", "completed", "cancelled", name="booking_status"
        ),
        server_default=None,
    )

    op.execute("UPDATE product_listings SET status = 'active' WHERE status = 'reserved'")
    op.execute("ALTER TYPE listing_status RENAME TO listing_status_old")
    postgresql.ENUM("active", "sold", "removed", name="listing_status").create(op.get_bind())
    op.execute(
        "ALTER TABLE product_listings ALTER COLUMN status "
        "TYPE listing_status USING status::text::listing_status"
    )
    op.execute("DROP TYPE listing_status_old")
