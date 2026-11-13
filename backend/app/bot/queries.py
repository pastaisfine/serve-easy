"""Read-only database access for the Telegram bot.

The bot gets its own engine so it can be locked to read-only transactions
without affecting the API's write routes. Every function returns the same
Pydantic schemas the HTTP API uses, so the bot cannot expose a field the API
hides (email, phone, student id).
"""

from collections.abc import Iterator
from contextlib import contextmanager
from decimal import Decimal

from sqlalchemy import create_engine, event, select
from sqlalchemy.orm import Session, joinedload, sessionmaker

from app.config import settings, to_sqlalchemy_url
from app.models import FoodItem, ProductListing, Service, Shop, User
from app.models.base import (
    ListingCategory,
    ListingCondition,
    ListingStatus,
    MealSession,
    ServiceCategory,
    UserRole,
)
from app.schemas import (
    CafeteriaOut,
    FoodItemOut,
    ListingOut,
    MenuOut,
    ServiceOut,
    ShopDetailOut,
    ShopOut,
)

# How many rows one Telegram page holds.
PAGE_SIZE = 5

_engine = create_engine(
    to_sqlalchemy_url(settings.database_url),
    pool_pre_ping=True,
    pool_recycle=300,
)


@event.listens_for(_engine, "begin")
def _read_only_transaction(conn) -> None:
    """Make every transaction on this engine read-only.

    Postgres then refuses any INSERT, UPDATE, DELETE or DDL from the bot,
    even if a handler has a bug. The flag is set per transaction rather than
    per connection because Neon hands each transaction to whichever pooled
    server connection is free, so a connection-level setting would not stick.
    """
    conn.exec_driver_sql("SET TRANSACTION READ ONLY")


_Session = sessionmaker(bind=_engine, expire_on_commit=False)


@contextmanager
def bot_session() -> Iterator[Session]:
    """A session whose transactions are all read-only."""
    with _Session() as session:
        yield session


def _like(term: str) -> str:
    """Escape the wildcards of a user-supplied search term."""
    escaped = term.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
    return f"%{escaped}%"


# ------------------------------------------------------------------ listings


def search_listings(
    session: Session,
    q: str | None = None,
    category: ListingCategory | None = None,
    condition: ListingCondition | None = None,
    max_price: Decimal | None = None,
    limit: int = PAGE_SIZE,
    offset: int = 0,
) -> list[ListingOut]:
    """Active listings, newest first. Mirrors `GET /listings`."""
    stmt = (
        select(ProductListing)
        .options(joinedload(ProductListing.seller), joinedload(ProductListing.shop))
        .where(ProductListing.status == ListingStatus.ACTIVE)
    )
    if category is not None:
        stmt = stmt.where(ProductListing.category == category)
    if condition is not None:
        stmt = stmt.where(ProductListing.condition == condition)
    if max_price is not None:
        stmt = stmt.where(ProductListing.price <= max_price)
    if q:
        stmt = stmt.where(ProductListing.title.ilike(_like(q), escape="\\"))
    stmt = stmt.order_by(ProductListing.created_at.desc(), ProductListing.id)
    stmt = stmt.limit(limit).offset(offset)
    return [ListingOut.model_validate(row) for row in session.scalars(stmt).all()]


def get_listing(session: Session, listing_id: str) -> ListingOut | None:
    """One listing. Removed ones are gone; sold ones stay viewable."""
    stmt = (
        select(ProductListing)
        .options(joinedload(ProductListing.seller), joinedload(ProductListing.shop))
        .where(ProductListing.id == listing_id, ProductListing.status != ListingStatus.REMOVED)
    )
    row = session.scalars(stmt).first()
    return ListingOut.model_validate(row) if row is not None else None


# ------------------------------------------------------------------ services


def search_services(
    session: Session,
    q: str | None = None,
    category: ServiceCategory | None = None,
    max_price: Decimal | None = None,
    limit: int = PAGE_SIZE,
    offset: int = 0,
) -> list[ServiceOut]:
    """Services, newest first. Mirrors `GET /services`."""
    stmt = (
        select(Service)
        .options(joinedload(Service.provider), joinedload(Service.shop))
    )
    if category is not None:
        stmt = stmt.where(Service.category == category)
    if max_price is not None:
        stmt = stmt.where(Service.price <= max_price)
    if q:
        stmt = stmt.where(Service.title.ilike(_like(q), escape="\\"))
    stmt = stmt.order_by(Service.created_at.desc(), Service.id)
    stmt = stmt.limit(limit).offset(offset)
    return [ServiceOut.model_validate(row) for row in session.scalars(stmt).all()]


def get_service(session: Session, service_id: str) -> ServiceOut | None:
    """One service."""
    stmt = (
        select(Service)
        .options(joinedload(Service.provider), joinedload(Service.shop))
        .where(Service.id == service_id)
    )
    row = session.scalars(stmt).first()
    return ServiceOut.model_validate(row) if row is not None else None


# ---------------------------------------------------------------- cafeterias


def list_cafeterias(session: Session) -> list[CafeteriaOut]:
    """The food sellers. Mirrors `GET /cafeterias`."""
    stmt = select(User).where(User.role == UserRole.FOOD_SELLER).order_by(User.name)
    return [CafeteriaOut.model_validate(row) for row in session.scalars(stmt).all()]


def find_cafeteria(session: Session, name: str) -> User | None:
    """The food seller whose name matches the search term."""
    stmt = (
        select(User)
        .where(User.role == UserRole.FOOD_SELLER, User.name.ilike(_like(name), escape="\\"))
        .order_by(User.name)
    )
    return session.scalars(stmt).first()


def get_menu(
    session: Session,
    cafeteria_id: str,
    meal_session: MealSession | None = None,
) -> MenuOut | None:
    """A cafeteria's available menu items. Mirrors `GET /cafeterias/{id}/menu`."""
    cafeteria = session.get(User, cafeteria_id)
    if cafeteria is None or cafeteria.role != UserRole.FOOD_SELLER:
        return None
    stmt = select(FoodItem).where(FoodItem.seller_id == cafeteria_id, FoodItem.available.is_(True))
    if meal_session is not None:
        stmt = stmt.where(FoodItem.meal_session == meal_session)
    stmt = stmt.order_by(FoodItem.meal_session, FoodItem.name)
    items = [FoodItemOut.model_validate(row) for row in session.scalars(stmt).all()]
    return MenuOut(cafeteria=CafeteriaOut.model_validate(cafeteria), items=items)


# --------------------------------------------------------------------- shops


def list_shops(session: Session) -> list[ShopOut]:
    """The student enterprises. Mirrors `GET /shops`."""
    stmt = select(Shop).options(joinedload(Shop.owner)).order_by(Shop.name)
    return [ShopOut.model_validate(row) for row in session.scalars(stmt).all()]


def find_shop(session: Session, name: str) -> Shop | None:
    """The shop whose name matches the search term."""
    stmt = (
        select(Shop)
        .options(joinedload(Shop.owner))
        .where(Shop.name.ilike(_like(name), escape="\\"))
        .order_by(Shop.name)
    )
    return session.scalars(stmt).first()


def get_shop(session: Session, shop_id: str) -> ShopDetailOut | None:
    """A shop with its active listings and services. Mirrors `GET /shops/{id}`."""
    shop = session.scalar(select(Shop).options(joinedload(Shop.owner)).where(Shop.id == shop_id))
    if shop is None:
        return None
    listing_rows = session.scalars(
        select(ProductListing)
        .options(joinedload(ProductListing.seller), joinedload(ProductListing.shop))
        .where(ProductListing.shop_id == shop_id, ProductListing.status == ListingStatus.ACTIVE)
        .order_by(ProductListing.created_at.desc(), ProductListing.id)
    ).all()
    service_rows = session.scalars(
        select(Service)
        .options(joinedload(Service.provider), joinedload(Service.shop))
        .where(Service.shop_id == shop_id)
        .order_by(Service.created_at.desc(), Service.id)
    ).all()
    return ShopDetailOut.model_validate(
        {
            "id": shop.id,
            "name": shop.name,
            "description": shop.description,
            "logo": shop.logo,
            "location": shop.location,
            "hours": shop.hours,
            "owner": shop.owner,
            "listings": [ListingOut.model_validate(row) for row in listing_rows],
            "services": [ServiceOut.model_validate(row) for row in service_rows],
        },
        from_attributes=True,
    )
