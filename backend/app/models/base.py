import enum
import uuid
from datetime import datetime
from decimal import Decimal
from typing import Annotated

from sqlalchemy import DateTime, Enum, Numeric, String, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

# Primary keys are strings so they stay compatible with Better Auth's string user ids.
str_pk = Annotated[str, mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))]
money = Annotated[Decimal, mapped_column(Numeric(10, 2))]
created_ts = Annotated[
    datetime, mapped_column(DateTime(timezone=True), server_default=func.now())
]


class Base(DeclarativeBase):
    pass


def pg_enum(enum_cls: type[enum.Enum], name: str) -> Enum:
    """Native Postgres enum that stores the member *values* (lowercase strings)."""
    return Enum(
        enum_cls,
        name=name,
        values_callable=lambda e: [m.value for m in e],
    )


class UserRole(enum.StrEnum):
    STUDENT = "student"
    FOOD_SELLER = "food_seller"
    SERVICE_PROVIDER = "service_provider"


class ListingCondition(enum.StrEnum):
    NEW = "new"
    LIKE_NEW = "like_new"
    GOOD = "good"
    FAIR = "fair"
    POOR = "poor"


class ListingCategory(enum.StrEnum):
    BOOKS = "books"
    ELECTRONICS = "electronics"
    CLOTHING = "clothing"
    KITCHEN = "kitchen"
    STATIONERY = "stationery"
    SPORTS = "sports"
    SNACKS = "snacks"
    DAILY_ESSENTIALS = "daily_essentials"
    HOBBIES = "hobbies"
    TICKETS = "tickets"
    OTHER = "other"


class ListingStatus(enum.StrEnum):
    ACTIVE = "active"
    RESERVED = "reserved"
    SOLD = "sold"
    REMOVED = "removed"


class MealSession(enum.StrEnum):
    LUNCH = "lunch"
    DINNER = "dinner"


class OrderStatus(enum.StrEnum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    READY = "ready"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class DeliveryStatus(enum.StrEnum):
    PREPARING = "preparing"
    ON_THE_WAY = "on_the_way"
    DELIVERED = "delivered"


class ServiceCategory(enum.StrEnum):
    PRINTING = "printing"
    TAILORING = "tailoring"
    REPAIR = "repair"
    GROOMING = "grooming"
    TUTORING = "tutoring"
    DESIGN = "design"
    MEDIA = "media"
    PROGRAMMING = "programming"
    ERRANDS = "errands"
    RENTALS = "rentals"
    OTHER = "other"


class BookingStatus(enum.StrEnum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    DECLINED = "declined"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class ProductOrderStatus(enum.StrEnum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    DECLINED = "declined"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


__all__ = [
    "Base",
    "Mapped",
    "mapped_column",
    "str_pk",
    "money",
    "created_ts",
    "pg_enum",
    "UserRole",
    "ListingCondition",
    "ListingCategory",
    "ListingStatus",
    "MealSession",
    "OrderStatus",
    "DeliveryStatus",
    "ServiceCategory",
    "BookingStatus",
    "ProductOrderStatus",
]
