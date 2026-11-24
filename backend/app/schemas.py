import re
from datetime import date, datetime
from decimal import Decimal
from typing import Annotated, Literal

from pydantic import AliasChoices, BaseModel, BeforeValidator, ConfigDict, Field, field_validator

from app.models.base import (
    DeliveryStatus,
    ListingCategory,
    ListingCondition,
    ListingStatus,
    MealSession,
    BookingStatus,
    ProductOrderStatus,
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
    """Public user details. Contact links are intentionally visible."""

    id: str
    name: str
    image: str | None
    faculty: str | None
    whatsapp: str | None = Field(validation_alias="phone")
    telegram_username: str | None


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
    whatsapp: str | None = Field(validation_alias=AliasChoices("whatsapp", "phone"))
    telegram_username: str | None


class FoodItemOut(ORM):
    id: str
    name: str
    price: Decimal
    meal_session: MealSession
    available: bool
    image: ImageUrl
    is_demo: bool


class MenuOut(BaseModel):
    cafeteria: CafeteriaOut
    items: list[FoodItemOut]


class MealOrderLineCreate(Create):
    item_id: str
    quantity: Annotated[int, Field(ge=1, le=20)]


class MealOrderCreate(Create):
    meal_session: MealSession
    pickup_location: Annotated[str, Field(min_length=1, max_length=120)]
    items: Annotated[list[MealOrderLineCreate], Field(min_length=1, max_length=100)]


class MealMenuItemCreate(Create):
    name: Annotated[str, Field(min_length=1, max_length=150)]
    price: Price
    meal_session: MealSession
    image: Annotated[str, Field(min_length=1, max_length=500)] | None = None


class MealMenuItemUpdate(Create):
    name: Annotated[str, Field(min_length=1, max_length=150)] | None = None
    price: Price | None = None
    meal_session: MealSession | None = None
    available: bool | None = None
    image: Annotated[str, Field(min_length=1, max_length=500)] | None = None


class MealProviderOut(ORM):
    id: str
    name: str
    image: ImageUrl
    whatsapp: str | None
    telegram_username: str | None


class MealDeliveryBatchOut(ORM):
    id: str
    provider_id: str
    meal_session: MealSession
    delivery_date: date
    pickup_location: str
    status: DeliveryStatus
    proof_image: ImageUrl
    delivered_at: datetime | None
    provider: MealProviderOut


class MealOrderLineOut(BaseModel):
    item_id: str
    name: str
    quantity: int
    unit_price: Decimal


class MealOrderOut(ORM):
    id: str
    total: Decimal
    status: str
    created_at: datetime
    provider: MealProviderOut
    meal_session: MealSession
    pickup_location: str
    delivery_batch: MealDeliveryBatchOut
    lines: list[MealOrderLineOut]


class MealOrderList(BaseModel):
    orders: list[MealOrderOut]


class MealBatchOrderLineOut(BaseModel):
    name: str
    quantity: int


class MealBatchOrderOut(BaseModel):
    id: str
    student_name: str
    total: Decimal
    lines: list[MealBatchOrderLineOut]


class ProviderDeliveryBatchOut(MealDeliveryBatchOut):
    orders: list[MealBatchOrderOut]


class MealDeliveryBatchUpdate(Create):
    status: DeliveryStatus
    proof_image: Annotated[str, Field(min_length=1, max_length=500)] | None = None


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


class ProductOrderCreate(Create):
    listing_id: str
    buyer_note: Annotated[str, Field(max_length=1000)] | None = None


class ProductOrderStatusUpdate(Create):
    status: ProductOrderStatus


class ProductOrderOut(BaseModel):
    id: str
    listing_id: str
    listing_title: str
    listing_image: ImageUrl
    price: Decimal
    meetup_spot: str
    buyer_note: str | None
    status: ProductOrderStatus
    created_at: datetime
    role: Literal["buying", "selling"]
    counterpart: UserSummary


class ServiceBookingCreate(Create):
    service_id: str
    details: Annotated[str, Field(min_length=1, max_length=5000)]
    requested_date: date


class ServiceBookingStatusUpdate(Create):
    status: BookingStatus


class ServiceBookingOut(BaseModel):
    id: str
    service_id: str
    service_title: str
    service_price: Decimal
    service_unit: str | None
    service_spot: str
    details: str
    requested_date: date
    status: BookingStatus
    created_at: datetime
    role: Literal["requesting", "providing"]
    counterpart: UserSummary


class NotificationOut(ORM):
    id: str
    notification_type: str
    title: str
    message: str
    href: str
    related_type: str
    related_id: str
    created_at: datetime
    read_at: datetime | None


class NotificationUnreadCount(BaseModel):
    count: int


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
    """The signed-in user's profile and public contact links."""

    id: str
    name: str
    email: str
    image: str | None
    faculty: str | None
    whatsapp: str | None = Field(validation_alias="phone")
    telegram_username: str | None
    role: UserRole
    shop: ShopRef | None


class ContactDetailsUpdate(Create):
    whatsapp: Annotated[str, Field(min_length=8, max_length=32)] | None = None
    telegram_username: Annotated[str, Field(min_length=5, max_length=32)] | None = None

    @field_validator("whatsapp", mode="before")
    @classmethod
    def normalize_whatsapp(cls, value: object) -> object:
        if not isinstance(value, str):
            return value
        value = value.strip()
        if not value:
            return None
        digits = re.sub(r"\D", "", value)
        if not 7 <= len(digits) <= 15 or not re.fullmatch(
            r"\+[1-9][0-9\s().-]*", value
        ):
            raise ValueError("Enter a valid phone number with its country code")
        return value

    @field_validator("telegram_username", mode="before")
    @classmethod
    def normalize_telegram_username(cls, value: object) -> object:
        if not isinstance(value, str):
            return value
        username = value.strip().removeprefix("@")
        if not username:
            return None
        if (
            not 5 <= len(username) <= 32
            or not username.isascii()
            or not username[0].isalpha()
            or not username.replace("_", "").isalnum()
        ):
            raise ValueError("Enter a valid Telegram username")
        return username


class RegistrationUpdate(Create):
    role: Literal["student", "service_provider", "food_seller"]
    food_provider_id: str | None = None
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
