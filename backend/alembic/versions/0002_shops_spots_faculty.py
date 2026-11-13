"""shops, meetup spots, faculty, service details, grooming/tutoring

Revision ID: 0002
Revises: 0001
Create Date: 2026-11-12

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0002"
down_revision: Union[str, Sequence[str], None] = "0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# Existing rows get this until the seed (or the owner) sets a real meetup spot.
SPOT_BACKFILL = "To be arranged"


def upgrade() -> None:
    # New service categories. Placed before 'other' so the enum order stays tidy.
    op.execute("ALTER TYPE service_category ADD VALUE IF NOT EXISTS 'grooming' BEFORE 'other'")
    op.execute("ALTER TYPE service_category ADD VALUE IF NOT EXISTS 'tutoring' BEFORE 'other'")

    op.add_column("users", sa.Column("faculty", sa.String(length=120), nullable=True))

    op.create_table(
        "shops",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("owner_id", sa.String(length=36), nullable=False),
        sa.Column("name", sa.String(length=150), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("logo", sa.String(length=500), nullable=True),
        sa.Column("location", sa.String(length=200), nullable=False),
        sa.Column("hours", sa.String(length=200), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["owner_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("owner_id"),
    )

    # product_listings
    op.add_column(
        "product_listings",
        sa.Column("spot", sa.String(length=200), nullable=False, server_default=SPOT_BACKFILL),
    )
    op.alter_column("product_listings", "spot", server_default=None)
    op.add_column("product_listings", sa.Column("shop_id", sa.String(length=36), nullable=True))
    op.create_foreign_key(
        "fk_product_listings_shop_id", "product_listings", "shops", ["shop_id"], ["id"], ondelete="SET NULL"
    )
    op.create_index(op.f("ix_product_listings_shop_id"), "product_listings", ["shop_id"], unique=False)

    # services
    op.add_column("services", sa.Column("unit", sa.String(length=30), nullable=True))
    op.add_column("services", sa.Column("image", sa.String(length=500), nullable=True))
    op.add_column(
        "services",
        sa.Column("spot", sa.String(length=200), nullable=False, server_default=SPOT_BACKFILL),
    )
    op.alter_column("services", "spot", server_default=None)
    op.add_column(
        "services",
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.add_column("services", sa.Column("shop_id", sa.String(length=36), nullable=True))
    op.create_foreign_key("fk_services_shop_id", "services", "shops", ["shop_id"], ["id"], ondelete="SET NULL")
    op.create_index(op.f("ix_services_shop_id"), "services", ["shop_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_services_shop_id"), table_name="services")
    op.drop_constraint("fk_services_shop_id", "services", type_="foreignkey")
    for column in ("shop_id", "created_at", "spot", "image", "unit"):
        op.drop_column("services", column)

    op.drop_index(op.f("ix_product_listings_shop_id"), table_name="product_listings")
    op.drop_constraint("fk_product_listings_shop_id", "product_listings", type_="foreignkey")
    op.drop_column("product_listings", "shop_id")
    op.drop_column("product_listings", "spot")

    op.drop_table("shops")
    op.drop_column("users", "faculty")
    # Postgres cannot drop enum values, so 'grooming' and 'tutoring' stay in
    # service_category after a downgrade. They are harmless when unused.
