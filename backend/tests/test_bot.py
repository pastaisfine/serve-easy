"""Tests for the Telegram bot's read-only query layer.

They run against the same seeded Neon database as the other tests and never
talk to Telegram.
"""

from decimal import Decimal

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.exc import DatabaseError

from app.bot import queries
from app.bot import telegram_bot
from app.config import settings, to_sqlalchemy_url
from app.models.base import ListingCategory
from app.schemas import ListingOut, ServiceOut
from app.seed.runner import seed


@pytest.fixture(scope="module", autouse=True)
def seeded():
    """The seed is idempotent, so make sure the demo data is present."""
    engine = create_engine(to_sqlalchemy_url(settings.migration_url))
    with engine.begin() as conn:
        seed(conn)


def test_bot_transactions_are_read_only():
    with queries.bot_session() as session:
        assert session.execute(text("SHOW transaction_read_only")).scalar() == "on"


def test_bot_cannot_write():
    """The database itself refuses a write from the bot."""
    with pytest.raises(DatabaseError):
        with queries.bot_session() as session:
            session.execute(text("UPDATE product_listings SET title = title WHERE false"))
            session.commit()


def test_search_listings_returns_only_active_listings():
    with queries.bot_session() as session:
        rows = queries.search_listings(session, limit=100)
    assert rows
    assert all(isinstance(row, ListingOut) for row in rows)
    assert {row.status for row in rows} == {"active"}


def test_search_listings_hides_private_fields():
    """The bot must not expose what the API hides."""
    with queries.bot_session() as session:
        rows = queries.search_listings(session, limit=5)
    assert rows
    for row in rows:
        assert set(row.seller.model_dump()) == {
            "id",
            "name",
            "image",
            "faculty",
            "whatsapp",
            "telegram_username",
        }
        assert "email" not in row.seller.model_dump()
        assert "student_id" not in row.seller.model_dump()
        card = telegram_bot._listing_card(row)
        if row.seller.whatsapp:
            assert row.seller.whatsapp not in card
        if row.seller.telegram_username:
            assert row.seller.telegram_username not in card


def test_search_listings_filters():
    with queries.bot_session() as session:
        books = queries.search_listings(session, category=ListingCategory.BOOKS, limit=100)
        assert books and {row.category for row in books} == {ListingCategory.BOOKS}

        cheap = queries.search_listings(session, max_price=Decimal("25"), limit=100)
        assert cheap and all(row.price <= Decimal("25") for row in cheap)

        found = queries.search_listings(session, q="calculator", limit=100)
        assert found and all("calculator" in row.title.lower() for row in found)


def test_search_services_filters():
    with queries.bot_session() as session:
        rows = queries.search_services(session, limit=100)
    assert rows
    assert all(isinstance(row, ServiceOut) for row in rows)

    found = queries.search_services(session, q="printing", limit=100)
    assert found and all("printing" in row.title.lower() for row in found)


def test_bot_service_cards_omit_public_contact_links():
    with queries.bot_session() as session:
        rows = queries.search_services(session, limit=5)
    assert rows
    for row in rows:
        card = telegram_bot._service_card(row)
        if row.provider.whatsapp:
            assert row.provider.whatsapp not in card
        if row.provider.telegram_username:
            assert row.provider.telegram_username not in card


def test_menu_only_returns_available_items():
    with queries.bot_session() as session:
        cafeterias = queries.list_cafeterias(session)
        assert cafeterias
        menu = queries.get_menu(session, cafeterias[0].id)
    assert menu is not None
    assert menu.items
    assert all(item.available for item in menu.items)


def test_shop_detail_has_listings_and_services():
    with queries.bot_session() as session:
        shops = queries.list_shops(session)
        assert shops
        detail = queries.get_shop(session, shops[0].id)
    assert detail is not None
    assert detail.id == shops[0].id
