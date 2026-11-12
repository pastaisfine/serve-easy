from sqlalchemy import ForeignKey, Index, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import (
    Base,
    ListingCategory,
    ListingCondition,
    ListingStatus,
    created_ts,
    money,
    pg_enum,
    str_pk,
)
from app.models.user import User


class ProductListing(Base):
    __tablename__ = "product_listings"
    __table_args__ = (
        Index("ix_product_listings_search", "status", "category", "price"),
    )

    id: Mapped[str_pk]
    seller_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    title: Mapped[str] = mapped_column(String(200))
    description: Mapped[str] = mapped_column(Text, default="")
    price: Mapped[money]
    condition: Mapped[ListingCondition] = mapped_column(pg_enum(ListingCondition, "listing_condition"))
    category: Mapped[ListingCategory] = mapped_column(pg_enum(ListingCategory, "listing_category"))
    image: Mapped[str | None] = mapped_column(String(500))
    status: Mapped[ListingStatus] = mapped_column(
        pg_enum(ListingStatus, "listing_status"), default=ListingStatus.ACTIVE
    )
    created_at: Mapped[created_ts]

    seller: Mapped[User] = relationship()
