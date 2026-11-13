"""drop 'furniture' listing category; add richer listing and service categories

Revision ID: 0003
Revises: 0002
Create Date: 2026-11-13

listing_category: Postgres cannot drop an enum value, so the type is recreated
(rename old, create new, convert the column, drop old). Any 'furniture' rows
become 'other' first.

service_category: only new values are added (ADD VALUE), as in 0002.

Existing rows keep their category. Re-running the seed re-categorises the demo
rows; rows created through the app stay where they are.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0003"
down_revision: Union[str, Sequence[str], None] = "0002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

LISTING_OLD = ("books", "electronics", "furniture", "clothing", "kitchen", "stationery", "sports", "other")
LISTING_NEW = (
    "books", "electronics", "clothing", "kitchen", "stationery", "sports",
    "snacks", "daily_essentials", "hobbies", "tickets", "other",
)
LISTING_ADDED = ("snacks", "daily_essentials", "hobbies", "tickets")
SERVICE_ADDED = ("design", "media", "programming", "errands", "rentals")


def _swap_listing_enum(values: tuple[str, ...]) -> None:
    """Recreate listing_category with `values` and convert the column to it."""
    op.execute("ALTER TYPE listing_category RENAME TO listing_category_old")
    sa.Enum(*values, name="listing_category").create(op.get_bind())
    op.execute(
        "ALTER TABLE product_listings ALTER COLUMN category "
        "TYPE listing_category USING category::text::listing_category"
    )
    op.execute("DROP TYPE listing_category_old")


def upgrade() -> None:
    op.execute("UPDATE product_listings SET category = 'other' WHERE category = 'furniture'")
    _swap_listing_enum(LISTING_NEW)

    for value in SERVICE_ADDED:
        op.execute(f"ALTER TYPE service_category ADD VALUE IF NOT EXISTS '{value}' BEFORE 'other'")


def downgrade() -> None:
    added = ", ".join(f"'{v}'" for v in LISTING_ADDED)
    op.execute(f"UPDATE product_listings SET category = 'other' WHERE category IN ({added})")
    _swap_listing_enum(LISTING_OLD)

    # Postgres cannot drop enum values, so the new service values stay in the
    # type after a downgrade; move the rows back to 'other' so none use them.
    service_added = ", ".join(f"'{v}'" for v in SERVICE_ADDED)
    op.execute(f"UPDATE services SET category = 'other' WHERE category IN ({service_added})")
