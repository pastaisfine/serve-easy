from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict

from app.models.base import (
    ListingCategory,
    ListingCondition,
    ListingStatus,
    MealSession,
    ServiceCategory,
)


class ORM(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class UserSummary(ORM):
    """The public slice of a user. Never exposes email, phone or student id."""

    id: str
    name: str
    image: str | None


class ListingOut(ORM):
    id: str
    title: str
    description: str
    price: Decimal
    condition: ListingCondition
    category: ListingCategory
    image: str | None
    status: ListingStatus
    created_at: datetime
    seller: UserSummary


class CafeteriaOut(ORM):
    id: str
    name: str
    image: str | None


class FoodItemOut(ORM):
    id: str
    name: str
    price: Decimal
    meal_session: MealSession
    available: bool
    image: str | None


class MenuOut(BaseModel):
    cafeteria: CafeteriaOut
    items: list[FoodItemOut]


class ServiceOut(ORM):
    id: str
    title: str
    description: str
    price: Decimal
    category: ServiceCategory
    provider: UserSummary

