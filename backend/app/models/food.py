from sqlalchemy import Boolean, CheckConstraint, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import (
    Base,
    MealSession,
    OrderStatus,
    created_ts,
    money,
    pg_enum,
    str_pk,
)
from app.models.user import User


class FoodItem(Base):
    __tablename__ = "food_items"

    id: Mapped[str_pk]
    seller_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    name: Mapped[str] = mapped_column(String(150))
    price: Mapped[money]
    meal_session: Mapped[MealSession] = mapped_column(pg_enum(MealSession, "meal_session"))
    available: Mapped[bool] = mapped_column(Boolean, default=True, server_default="true")
    image: Mapped[str | None] = mapped_column(String(500))

    seller: Mapped[User] = relationship()


class FoodOrder(Base):
    __tablename__ = "food_orders"

    id: Mapped[str_pk]
    buyer_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    seller_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    total: Mapped[money]
    pickup_note: Mapped[str | None] = mapped_column(Text)
    payment_ref: Mapped[str | None] = mapped_column(String(100))
    payment_proof: Mapped[str | None] = mapped_column(String(500))
    status: Mapped[OrderStatus] = mapped_column(
        pg_enum(OrderStatus, "order_status"), default=OrderStatus.PENDING
    )
    created_at: Mapped[created_ts]

    buyer: Mapped[User] = relationship(foreign_keys=[buyer_id])
    seller: Mapped[User] = relationship(foreign_keys=[seller_id])
    lines: Mapped[list["OrderLineItem"]] = relationship(
        back_populates="order", cascade="all, delete-orphan"
    )


class OrderLineItem(Base):
    __tablename__ = "order_line_items"
    __table_args__ = (CheckConstraint("quantity > 0", name="ck_order_line_items_quantity_positive"),)

    id: Mapped[str_pk]
    order_id: Mapped[str] = mapped_column(
        ForeignKey("food_orders.id", ondelete="CASCADE"), index=True
    )
    item_id: Mapped[str] = mapped_column(ForeignKey("food_items.id", ondelete="RESTRICT"), index=True)
    quantity: Mapped[int] = mapped_column(Integer)
    unit_price: Mapped[money]

    order: Mapped[FoodOrder] = relationship(back_populates="lines")
    item: Mapped[FoodItem] = relationship()
