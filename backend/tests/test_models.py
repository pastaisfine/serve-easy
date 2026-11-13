from app.models import Base


def test_metadata_contains_all_prd_entities():
    assert set(Base.metadata.tables) == {
        "users",
        "shops",
        "product_listings",
        "food_items",
        "food_orders",
        "order_line_items",
        "services",
        "service_bookings",
        "messages",
    }
