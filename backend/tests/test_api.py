import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine

from app.config import settings, to_sqlalchemy_url
from app.main import app
from app.seed import data
from app.seed.runner import seed


@pytest.fixture(scope="module", autouse=True)
def seeded():
    """The seed is idempotent, so make sure the demo data is present."""
    engine = create_engine(to_sqlalchemy_url(settings.migration_url))
    with engine.begin() as conn:
        seed(conn)


@pytest.fixture(scope="module")
def client():
    return TestClient(app)


KAK_MIN = data.uid("user", "kakmin.kitchen")


def test_listings_returns_only_active_with_public_seller_fields(client):
    res = client.get("/listings?limit=100")
    assert res.status_code == 200
    body = res.json()
    assert len(body) == 24  # 25 seeded, 1 sold
    assert {l["status"] for l in body} == {"active"}
    assert set(body[0]["seller"]) == {"id", "name", "image"}  # no email/phone leaked


def test_listings_filters(client):
    books = client.get("/listings?category=books").json()
    assert books and {l["category"] for l in books} == {"books"}

    cheap = client.get("/listings?max_price=25&limit=100").json()
    assert cheap and all(float(l["price"]) <= 25 for l in cheap)

    ranged = client.get("/listings?min_price=40&max_price=60&condition=good&limit=100").json()
    assert ranged and all(40 <= float(l["price"]) <= 60 and l["condition"] == "good" for l in ranged)

    found = client.get("/listings?q=calculator").json()
    assert [l["title"] for l in found] == ["Casio FX-570EX Scientific Calculator"]


def test_listings_search_treats_wildcards_literally(client):
    assert client.get("/listings?q=%25").json() == []


def test_listings_pagination_and_validation(client):
    first = client.get("/listings?limit=5").json()
    second = client.get("/listings?limit=5&offset=5").json()
    assert len(first) == len(second) == 5
    assert not {l["id"] for l in first} & {l["id"] for l in second}
    assert client.get("/listings?category=nope").status_code == 422
    assert client.get("/listings?limit=1000").status_code == 422


def test_cafeterias_lists_the_four_food_sellers(client):
    names = [c["name"] for c in client.get("/cafeterias").json()]
    assert len(names) == 4 and "Kak Min" in names


def test_menu_shows_available_items_and_filters_by_session(client):
    menu = client.get(f"/cafeterias/{KAK_MIN}/menu").json()
    assert menu["cafeteria"]["name"] == "Kak Min"
    assert len(menu["items"]) == 6

    dinner = client.get(f"/cafeterias/{KAK_MIN}/menu?meal_session=dinner").json()["items"]
    assert dinner and {i["meal_session"] for i in dinner} == {"dinner"}

    pak_lah = client.get(f"/cafeterias/{data.uid('user', 'paklah.warung')}/menu").json()
    assert "Air Bandung" not in [i["name"] for i in pak_lah["items"]]  # unavailable


def test_menu_404_for_unknown_or_non_cafeteria(client):
    assert client.get("/cafeterias/does-not-exist/menu").status_code == 404
    student = data.uid("user", "aisyah.rahman")
    assert client.get(f"/cafeterias/{student}/menu").status_code == 404


def test_services(client):
    everything = client.get("/services").json()
    assert len(everything) == 7
    repairs = client.get("/services?category=repair").json()
    assert len(repairs) == 3 and {s["category"] for s in repairs} == {"repair"}
    assert set(everything[0]["provider"]) == {"id", "name", "image"}
