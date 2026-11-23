from decimal import Decimal

from sqlalchemy import CheckConstraint, ForeignKey, Index, Numeric, String, Text, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import (
    Base,
    ProductOrderStatus,
    created_ts,
    pg_enum,
    str_pk,
)
from app.models.marketplace import ProductListing
from app.models.user import User


class ProductOrder(Base):
    __tablename__ = "product_orders"
    __table_args__ = (
        CheckConstraint("buyer_id <> seller_id", name="ck_product_orders_no_self_purchase"),
        Index(
            "uq_product_orders_active_listing",
            "listing_id",
            unique=True,
            postgresql_where=text("status IN ('pending', 'accepted')"),
            sqlite_where=text("status IN ('pending', 'accepted')"),
        ),
    )

    id: Mapped[str_pk]
    listing_id: Mapped[str] = mapped_column(
        ForeignKey("product_listings.id", ondelete="RESTRICT"), index=True
    )
    buyer_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    seller_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    listing_title: Mapped[str] = mapped_column(String(200))
    listing_image: Mapped[str | None] = mapped_column(String(500))
    price: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    meetup_spot: Mapped[str] = mapped_column(String(200))
    buyer_note: Mapped[str | None] = mapped_column(Text)
    status: Mapped[ProductOrderStatus] = mapped_column(
        pg_enum(ProductOrderStatus, "product_order_status"),
        default=ProductOrderStatus.PENDING,
        server_default=ProductOrderStatus.PENDING.value,
    )
    created_at: Mapped[created_ts]

    listing: Mapped[ProductListing] = relationship(back_populates="orders")
    buyer: Mapped[User] = relationship(foreign_keys=[buyer_id])
    seller: Mapped[User] = relationship(foreign_keys=[seller_id])
