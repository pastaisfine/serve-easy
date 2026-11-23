from app.models import Base


def test_metadata_contains_all_prd_entities():
    assert set(Base.metadata.tables) == {
        "users",
        "shops",
        "product_listings",
        "product_orders",
        "food_providers",
        "food_provider_staff",
        "food_items",
        "food_orders",
        "food_delivery_batches",
        "order_line_items",
        "services",
        "service_bookings",
        "messages",
    }
