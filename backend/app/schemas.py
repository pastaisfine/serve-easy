from datetime import datetime
from decimal import Decimal
from typing import Annotated, Literal

from pydantic import BaseModel, BeforeValidator, ConfigDict, Field, field_validator

from app.models.base import (
    ListingCategory,
    ListingCondition,
    ListingStatus,
    MealSession,
    ServiceCategory,
    UserRole,
)
from app.storage import public_url


class ORM(BaseModel):
    model_config = ConfigDict(from_attributes=True)


# A stored image is either a full URL (seed data) or an object key (uploads).
# Output always shows a URL.
ImageUrl = Annotated[str | None, BeforeValidator(public_url)]

# Largest value the numeric(10, 2) price column holds is 99,999,999.99; cap well below it.
Price = Annotated[Decimal, Field(gt=0, le=Decimal("99999.99"), max_digits=7, decimal_places=2)]


class Create(BaseModel):
    """Base for request bodies: trim strings and reject unknown fields."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


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
    image: ImageUrl
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
    image: ImageUrl
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


# ---------------------------------------------------------------- write models


class ListingCreate(Create):
    title: Annotated[str, Field(min_length=1, max_length=200)]
    description: Annotated[str, Field(max_length=5000)] = ""
    price: Price
    condition: ListingCondition
    category: ListingCategory
    # Object key returned by POST /uploads/images. Arbitrary URLs are rejected.
    image: Annotated[str, Field(min_length=1, max_length=500)] | None = None
    spot: Annotated[str, Field(min_length=1, max_length=200)]
    # Must be the caller's own shop.
    shop_id: str | None = None


class ServiceCreate(Create):
    title: Annotated[str, Field(min_length=1, max_length=200)]
    description: Annotated[str, Field(max_length=5000)] = ""
    price: Price
    unit: Annotated[str, Field(min_length=1, max_length=30)] | None = None  # "hour", "page"
    category: ServiceCategory
    image: Annotated[str, Field(min_length=1, max_length=500)] | None = None
    spot: Annotated[str, Field(min_length=1, max_length=200)]
    shop_id: str | None = None


class MeOut(ORM):
    """The signed-in user, including the private fields `UserSummary` hides."""

    id: str
    name: str
    email: str
    image: str | None
    faculty: str | None
    role: UserRole
    shop: ShopRef | None


class RegistrationUpdate(Create):
    role: Literal["student", "service_provider"]
    student_id: Annotated[
        str, Field(min_length=9, max_length=9, pattern=r"^A[0-9]{2}[A-Z]{2}[0-9]{4}$")
    ] | None = None

    @field_validator("student_id", mode="before")
    @classmethod
    def normalize_student_id(cls, value: object) -> object:
        return value.upper() if isinstance(value, str) else value


class UploadOut(BaseModel):
    key: str
    url: str
