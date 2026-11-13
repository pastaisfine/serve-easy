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


def _all(client, path):
    """Collect every row by paging, since the API caps limit at 100."""
    rows, offset = [], 0
    sep = "&" if "?" in path else "?"
    while True:
        page = client.get(f"{path}{sep}limit=100&offset={offset}").json()
        rows += page
        if len(page) < 100:
            return rows
        offset += 100


def test_listings_returns_only_active_with_public_seller_fields(client):
    assert client.get("/listings?limit=100").status_code == 200
    body = _all(client, "/listings")
    assert len(body) == sum(1 for r in data.LISTINGS if r["status"] == "active")
    assert {l["status"] for l in body} == {"active"}
    assert set(body[0]["seller"]) == {"id", "name", "image", "faculty"}  # no email/phone leaked
    assert all(l["spot"] for l in body)


def test_listings_filters(client):
    books = client.get("/listings?category=books").json()
    assert books and {l["category"] for l in books} == {"books"}

    cheap = client.get("/listings?max_price=25&limit=100").json()
    assert cheap and all(float(l["price"]) <= 25 for l in cheap)

    ranged = client.get("/listings?min_price=40&max_price=60&condition=good&limit=100").json()
    assert ranged and all(40 <= float(l["price"]) <= 60 and l["condition"] == "good" for l in ranged)

    found = client.get("/listings?q=calculator").json()
    assert "Casio FX-570EX Scientific Calculator" in [l["title"] for l in found]


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
    everything = _all(client, "/services")
    assert len(everything) == len(data.SERVICES)
    repairs = _all(client, "/services?category=repair")
    assert len(repairs) == sum(1 for r in data.SERVICES if r["category"] == "repair") and {s["category"] for s in repairs} == {"repair"}
    assert set(everything[0]["provider"]) == {"id", "name", "image", "faculty"}
    assert all(s["spot"] for s in everything)


def test_services_search_by_title(client):
    found = client.get("/services?q=printing").json()
    assert {"Black & White Printing", "Colour Printing & Poster A3"} <= {s["title"] for s in found}
    combined = client.get("/services?q=printing&category=repair").json()
    assert combined == []
    assert client.get("/services?q=zzz-no-such-service").json() == []


def test_services_search_treats_wildcards_literally(client):
    assert client.get("/services?q=%25").json() == []
    assert client.get("/services?q=_").json() == []
    assert client.get("/services?q=").status_code == 422


def test_new_service_categories_and_fields(client):
    grooming = client.get("/services?category=grooming").json()
    assert "Haircut at your kolej" in [s["title"] for s in grooming]
    assert all(s["unit"] and s["spot"] for s in grooming)
    assert client.get("/services?category=tutoring").json()
    created = [s["created_at"] for s in client.get("/services").json()]
    assert created == sorted(created, reverse=True)  # newest first


def test_shops_list_and_the_cube(client):
    shops = client.get("/shops").json()
    assert [s["name"] for s in shops] == ["Amir Print Corner", "Nadia's Stitches", "The Cube"]
    cube = next(s for s in shops if s["name"] == "The Cube")
    assert cube["hours"] == "7:00 PM - 11:30 PM, daily"
    assert set(cube["owner"]) == {"id", "name", "image", "faculty"}


def test_shop_detail_includes_its_services_and_links_back_from_them(client):
    shops = client.get("/shops").json()
    amir = next(s for s in shops if s["name"] == "Amir Print Corner")
    detail = client.get(f"/shops/{amir['id']}").json()
    assert {s["title"] for s in detail["services"]} == {
        "Black & White Printing",
        "Colour Printing & Poster A3",
        "Thesis & Report Binding",
    }
    assert detail["listings"] == []
    # reachable from a listing/service: the shop ref carries the id to link to
    printing = [s for s in _all(client, "/services?category=printing") if s["shop"]]
    assert all(s["shop"]["id"] == amir["id"] for s in printing)

    cube = next(s for s in shops if s["name"] == "The Cube")
    assert client.get(f"/shops/{cube['id']}").json()["services"] == []


def test_shop_404(client):
    assert client.get("/shops/does-not-exist").status_code == 404


def test_new_listing_categories_filter_and_furniture_is_rejected(client):
    for category in ("snacks", "daily_essentials", "hobbies", "tickets"):
        rows = _all(client, f"/listings?category={category}")
        assert rows and {r["category"] for r in rows} == {category}
    assert client.get("/listings?category=furniture").status_code == 422


def test_new_service_categories_filter(client):
    for category in ("design", "media", "programming", "errands", "rentals"):
        rows = _all(client, f"/services?category={category}")
        assert rows and {r["category"] for r in rows} == {category}
