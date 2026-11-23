from datetime import date, datetime

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Date,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import (
    Base,
    DeliveryStatus,
    MealSession,
    OrderStatus,
    created_ts,
    money,
    pg_enum,
    str_pk,
)
from app.models.user import User


class FoodProvider(Base):
    __tablename__ = "food_providers"

    id: Mapped[str_pk]
    name: Mapped[str] = mapped_column(String(120), unique=True)
    image: Mapped[str | None] = mapped_column(String(500))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, server_default="true")
    created_at: Mapped[created_ts]

    staff: Mapped[list["FoodProviderStaff"]] = relationship(
        back_populates="provider", cascade="all, delete-orphan"
    )


class FoodProviderStaff(Base):
    __tablename__ = "food_provider_staff"
    __table_args__ = (
        UniqueConstraint("provider_id", "user_id", name="uq_food_provider_staff_provider_user"),
    )

    id: Mapped[str_pk]
    provider_id: Mapped[str] = mapped_column(
        ForeignKey("food_providers.id", ondelete="CASCADE"), index=True
    )
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)

    provider: Mapped[FoodProvider] = relationship(back_populates="staff")
    user: Mapped[User] = relationship()


class FoodItem(Base):
    __tablename__ = "food_items"

    id: Mapped[str_pk]
    seller_id: Mapped[str | None] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    provider_id: Mapped[str | None] = mapped_column(
        ForeignKey("food_providers.id", ondelete="CASCADE"), index=True
    )
    name: Mapped[str] = mapped_column(String(150))
    price: Mapped[money]
    meal_session: Mapped[MealSession] = mapped_column(pg_enum(MealSession, "meal_session"))
    available: Mapped[bool] = mapped_column(Boolean, default=True, server_default="true")
    image: Mapped[str | None] = mapped_column(String(500))
    is_demo: Mapped[bool] = mapped_column(Boolean, default=False, server_default="false")

    seller: Mapped[User | None] = relationship()
    provider: Mapped[FoodProvider | None] = relationship()


class FoodOrder(Base):
    __tablename__ = "food_orders"

    id: Mapped[str_pk]
    buyer_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    seller_id: Mapped[str | None] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    provider_id: Mapped[str | None] = mapped_column(
        ForeignKey("food_providers.id", ondelete="SET NULL"), index=True
    )
    delivery_batch_id: Mapped[str | None] = mapped_column(
        ForeignKey("food_delivery_batches.id", ondelete="SET NULL"), index=True
    )
    total: Mapped[money]
    pickup_note: Mapped[str | None] = mapped_column(Text)
    payment_ref: Mapped[str | None] = mapped_column(String(100))
    payment_proof: Mapped[str | None] = mapped_column(String(500))
    status: Mapped[OrderStatus] = mapped_column(
        pg_enum(OrderStatus, "order_status"), default=OrderStatus.PENDING
    )
    created_at: Mapped[created_ts]

    buyer: Mapped[User] = relationship(foreign_keys=[buyer_id])
    seller: Mapped[User | None] = relationship(foreign_keys=[seller_id])
    provider: Mapped[FoodProvider | None] = relationship()
    delivery_batch: Mapped["FoodDeliveryBatch | None"] = relationship(
        foreign_keys=[delivery_batch_id], back_populates="orders"
    )
    lines: Mapped[list["OrderLineItem"]] = relationship(
        back_populates="order", cascade="all, delete-orphan"
    )

    @property
    def meal_session(self) -> MealSession | None:
        return self.delivery_batch.meal_session if self.delivery_batch else None

    @property
    def pickup_location(self) -> str | None:
        return self.delivery_batch.pickup_location if self.delivery_batch else None

    @property
    def student_name(self) -> str:
        return self.buyer.name


class FoodDeliveryBatch(Base):
    __tablename__ = "food_delivery_batches"
    __table_args__ = (
        UniqueConstraint(
            "provider_id",
            "meal_session",
            "delivery_date",
            "pickup_location",
            name="uq_food_delivery_batch_scope",
        ),
    )

    id: Mapped[str_pk]
    provider_id: Mapped[str] = mapped_column(
        ForeignKey("food_providers.id", ondelete="CASCADE"), index=True
    )
    meal_session: Mapped[MealSession] = mapped_column(pg_enum(MealSession, "meal_session"))
    delivery_date: Mapped[date] = mapped_column(Date, index=True)
    pickup_location: Mapped[str] = mapped_column(String(120))
    status: Mapped[DeliveryStatus] = mapped_column(
        pg_enum(DeliveryStatus, "delivery_status"),
        default=DeliveryStatus.PREPARING,
        server_default=DeliveryStatus.PREPARING.value,
    )
    proof_image: Mapped[str | None] = mapped_column(String(500))
    delivered_at: Mapped[datetime | None] = mapped_column(nullable=True)
    created_at: Mapped[created_ts]

    provider: Mapped[FoodProvider] = relationship()
    orders: Mapped[list[FoodOrder]] = relationship(back_populates="delivery_batch")


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
    item_name: Mapped[str | None] = mapped_column(String(150))

    order: Mapped[FoodOrder] = relationship(back_populates="lines")
    item: Mapped[FoodItem] = relationship()

    @property
    def name(self) -> str:
        return self.item_name or self.item.name
