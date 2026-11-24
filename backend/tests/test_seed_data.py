from decimal import Decimal

from app.models import Base
from app.models.base import UserRole
from app.seed import data


def _ids(rows):
    return {r["id"] for r in rows}


def test_every_table_is_registered_and_non_empty():
    names = [name for name, _ in data.TABLES]
    assert set(names) == set(Base.metadata.tables)
    assert len(names) == len(set(names))
    intentionally_empty = {
        "food_provider_staff",
        "food_delivery_batches",
        "product_orders",
        "notifications",
    }
    assert all(rows or name in intentionally_empty for name, rows in data.TABLES)


def test_ids_are_unique_per_table_and_deterministic():
    for name, rows in data.TABLES:
        assert len(_ids(rows)) == len(rows), f"duplicate ids in {name}"
    assert data.uid("user", "x") == data.uid("user", "x")
    assert data.uid("user", "x") != data.uid("food", "x")


def test_rows_only_use_real_columns_and_required_columns_are_set():
    for name, rows in data.TABLES:
        table = Base.metadata.tables[name]
        required = {
            c.name
            for c in table.columns
            if not c.nullable and c.server_default is None and c.default is None
        }
        for row in rows:
            assert set(row) <= set(table.columns.keys()), f"{name}: unknown column"
            assert required <= set(row), f"{name}: missing {required - set(row)}"


def test_foreign_keys_resolve():
    for name, rows in data.TABLES:
        table = Base.metadata.tables[name]
        targets = {
            fk.parent.name: (fk.column.table.name, fk.column.name)
            for fk in table.foreign_keys
        }
        lookup = dict(data.TABLES)
        for row in rows:
            for column, (target_table, target_col) in targets.items():
                if row.get(column) is None:
                    assert table.columns[column].nullable, f"{name}.{column} is required"
                    continue
                valid = {r[target_col] for r in lookup[target_table]}
                assert row[column] in valid, f"{name}.{column} -> {target_table} is dangling"


def test_tables_are_ordered_parents_first():
    seen: set[str] = set()
    for name, _ in data.TABLES:
        for fk in Base.metadata.tables[name].foreign_keys:
            parent = fk.column.table.name
            assert parent in seen or parent == name, f"{name} comes before {parent}"
        seen.add(name)


def test_order_totals_equal_sum_of_line_items():
    for order in data.FOOD_ORDERS:
        lines = [l for l in data.ORDER_LINE_ITEMS if l["order_id"] == order["id"]]
        assert lines, "every order has at least one line"
        assert order["total"] == sum(l["unit_price"] * l["quantity"] for l in lines)


def test_line_items_belong_to_the_orders_seller_and_use_menu_prices():
    items = {i["id"]: i for i in data.FOOD_ITEMS}
    orders = {o["id"]: o for o in data.FOOD_ORDERS}
    for line in data.ORDER_LINE_ITEMS:
        item = items[line["item_id"]]
        assert item["seller_id"] == orders[line["order_id"]]["seller_id"]
        assert line["unit_price"] == item["price"]
        assert line["quantity"] > 0


def test_roles_match_how_users_are_used():
    role = {u["id"]: u["role"] for u in data.USERS}
    assert all(role[l["seller_id"]] == UserRole.STUDENT for l in data.LISTINGS)
    legacy_items = [item for item in data.FOOD_ITEMS if item.get("seller_id")]
    sample_items = [item for item in data.FOOD_ITEMS if item.get("provider_id")]
    assert all(role[i["seller_id"]] == UserRole.FOOD_SELLER for i in legacy_items)
    providers = {provider["id"] for provider in data.FOOD_PROVIDERS}
    assert all(item["provider_id"] in providers for item in sample_items)
    assert all(item["is_demo"] for item in sample_items)
    assert all(role[o["seller_id"]] == UserRole.FOOD_SELLER for o in data.FOOD_ORDERS)
    assert all(role[o["buyer_id"]] == UserRole.STUDENT for o in data.FOOD_ORDERS)
    assert all(role[s["provider_id"]] == UserRole.SERVICE_PROVIDER for s in data.SERVICES)
    assert all(role[b["student_id"]] == UserRole.STUDENT for b in data.SERVICE_BOOKINGS)


def test_unique_columns_do_not_collide():
    emails = [u["email"] for u in data.USERS]
    student_ids = [u["student_id"] for u in data.USERS if u["student_id"]]
    assert len(emails) == len(set(emails))
    assert len(student_ids) == len(set(student_ids))


def test_prices_are_positive():
    for rows in (data.LISTINGS, data.FOOD_ITEMS, data.SERVICES):
        assert all(r["price"] > Decimal("0") for r in rows)


def test_demo_set_is_the_agreed_size():
    counts = data.summary()
    assert 10 <= counts["users"] <= 60
    assert 200 <= counts["product_listings"] <= 260
    assert 200 <= counts["services"] <= 260
    sellers = {i["seller_id"] for i in data.FOOD_ITEMS if i.get("seller_id")}
    assert 3 <= len(sellers) <= 4


def test_meal_sample_menu_has_the_three_requested_providers():
    assert {provider["name"] for provider in data.FOOD_PROVIDERS} == {
        "JojoeKopitiam",
        "芬姐",
        "吉宝",
    }
    assert all(
        item["meal_session"] in {"lunch", "dinner"}
        and item["price"] > Decimal("0")
        for item in data.FOOD_ITEMS
        if item.get("provider_id")
    )


def test_every_listing_and_service_has_a_meetup_spot():
    for row in data.LISTINGS + data.SERVICES:
        assert row["spot"].strip(), row


def test_the_cube_shop_has_the_details_supplied_by_the_owner():
    cube = next(s for s in data.SHOPS if s["name"] == "The Cube")
    assert cube["location"].startswith("Lot 6, Student Mall")
    assert cube["hours"] == "7:00 PM - 11:30 PM, daily"
    assert "shaved ice" in cube["description"]
    assert "tea eggs" in cube["description"]
    assert "shao xian cao" in cube["description"]


def test_each_student_owns_at_most_one_shop_and_owners_are_not_cafeterias():
    owners = [s["owner_id"] for s in data.SHOPS]
    assert len(owners) == len(set(owners))
    role = {u["id"]: u["role"] for u in data.USERS}
    assert all(role[o] != UserRole.FOOD_SELLER for o in owners)


def test_services_cover_grooming_and_tutoring():
    categories = {s["category"].value for s in data.SERVICES}
    assert {"grooming", "tutoring", "printing", "tailoring", "repair"} <= categories


def test_student_like_users_have_a_faculty():
    for user in data.USERS:
        if user["role"] != UserRole.FOOD_SELLER:
            assert user["faculty"], user["name"]


def test_listings_and_services_use_frontend_allowed_image_hosts():
    for row in data.LISTINGS + data.SERVICES:
        assert row["image"].startswith("https://images.unsplash.com/"), row["image"]


def test_every_category_except_other_has_seed_rows():
    from app.models.base import ListingCategory, ServiceCategory

    used_items = {r["category"] for r in data.LISTINGS}
    used_services = {r["category"] for r in data.SERVICES}
    for cat in ListingCategory:
        if cat is not ListingCategory.OTHER:
            assert cat in used_items, f"no listing for {cat}"
    for cat in ServiceCategory:
        if cat is not ServiceCategory.OTHER:
            assert cat in used_services, f"no service for {cat}"


def test_furniture_category_is_gone():
    from app.models.base import ListingCategory

    assert "furniture" not in {c.value for c in ListingCategory}


def test_every_photo_group_has_usable_reviewed_photos():
    from app.seed import photo_groups, photos

    for group in photo_groups.GROUPS:
        assert photos._usable(group), f"photo group {group!r} has no usable cached photos"
    for group, bad in photos._rejects.items():
        assert group in photo_groups.GROUPS, f"rejects for unknown group {group!r}"
        assert all(0 <= i < photos.REVIEWED for i in bad), f"reject index out of range in {group!r}"


def test_every_listing_and_service_photo_is_an_unsplash_url_the_frontend_allows():
    for row in data.LISTINGS + data.SERVICES:
        assert row["image"].startswith("https://images.unsplash.com/photo-"), row["image"]
