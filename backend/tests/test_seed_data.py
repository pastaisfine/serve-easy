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
    assert all(rows for _, rows in data.TABLES)


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
    assert all(role[i["seller_id"]] == UserRole.FOOD_SELLER for i in data.FOOD_ITEMS)
    assert all(role[o["seller_id"]] == UserRole.FOOD_SELLER for o in data.FOOD_ORDERS)
    assert all(role[o["buyer_id"]] == UserRole.STUDENT for o in data.FOOD_ORDERS)
    assert all(role[s["provider_id"]] == UserRole.SERVICE_PROVIDER for s in data.SERVICES)
    assert all(role[b["student_id"]] == UserRole.STUDENT for b in data.SERVICE_BOOKINGS)


def test_unique_columns_do_not_collide():
    emails = [u["email"] for u in data.USERS]
    student_ids = [u["student_id"] for u in data.USERS if u["student_id"]]
    assert len(emails) == len(set(emails))
    assert len(student_ids) == len(set(student_ids))


def test_no_message_is_sent_to_self_and_prices_are_positive():
    assert all(m["sender_id"] != m["receiver_id"] for m in data.MESSAGES)
    for rows in (data.LISTINGS, data.FOOD_ITEMS, data.SERVICES):
        assert all(r["price"] > Decimal("0") for r in rows)


def test_demo_set_is_the_agreed_size():
    counts = data.summary()
    assert 10 <= counts["users"] <= 15
    assert 20 <= counts["product_listings"] <= 30
    assert 5 <= counts["services"] <= 8
    sellers = {i["seller_id"] for i in data.FOOD_ITEMS}
    assert 3 <= len(sellers) <= 4
