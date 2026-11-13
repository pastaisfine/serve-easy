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
    faculty: str | None


class ShopRef(ORM):
    """Just enough to link from a listing to its shop page."""

    id: str
    name: str
    logo: str | None


class ListingOut(ORM):
    id: str
    title: str
    description: str
    price: Decimal
    condition: ListingCondition
    category: ListingCategory
    image: str | None
    spot: str
    status: ListingStatus
    created_at: datetime
    seller: UserSummary
    shop: ShopRef | None


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
    unit: str | None
    category: ServiceCategory
    image: str | None
    spot: str
    created_at: datetime
    provider: UserSummary
    shop: ShopRef | None


class ShopOut(ORM):
    id: str
    name: str
    description: str
    logo: str | None
    location: str
    hours: str | None
    owner: UserSummary


class ShopDetailOut(ShopOut):
    listings: list[ListingOut]
    services: list[ServiceOut]
