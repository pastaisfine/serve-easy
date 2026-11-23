from datetime import date, timedelta
from decimal import Decimal

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.auth import current_user
from app.db import get_db
from app.main import app
from app.models import Base, ProductListing, Service, ServiceBooking, User
from app.models.base import (
    BookingStatus,
    ListingCategory,
    ListingCondition,
    ListingStatus,
    ServiceCategory,
    UserRole,
)


@pytest.fixture
def request_client():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    factory = sessionmaker(bind=engine, expire_on_commit=False)
    actors: dict[str, User] = {}

    with factory() as db:
        student = User(
            id="student-1",
            name="Student One",
            email="student@example.test",
            role=UserRole.STUDENT,
        )
        another_student = User(
            id="student-2",
            name="Student Two",
            email="student2@example.test",
            role=UserRole.STUDENT,
        )
        seller = User(
            id="seller-1",
            name="Seller One",
            email="seller@example.test",
            role=UserRole.STUDENT,
        )
        provider = User(
            id="provider-1",
            name="Provider One",
            email="provider@example.test",
            role=UserRole.SERVICE_PROVIDER,
        )
        db.add_all([student, another_student, seller, provider])
        db.flush()
        db.add_all(
            [
                ProductListing(
                    id="listing-1",
                    seller_id=seller.id,
                    title="Used textbook",
                    description="A textbook",
                    price=Decimal("25.00"),
                    condition=ListingCondition.GOOD,
                    category=ListingCategory.BOOKS,
                    spot="Library entrance",
                    status=ListingStatus.ACTIVE,
                ),
                Service(
                    id="service-1",
                    provider_id=provider.id,
                    title="Math tutoring",
                    description="One-to-one tutoring",
                    price=Decimal("20.00"),
                    unit="hour",
                    category=ServiceCategory.TUTORING,
                    spot="Campus library",
                ),
                Service(
                    id="service-2",
                    provider_id=student.id,
                    title="Study notes",
                    description="Notes for a course",
                    price=Decimal("5.00"),
                    unit=None,
                    category=ServiceCategory.OTHER,
                    spot="Online",
                ),
            ]
        )
        db.commit()
        actors.update(
            student=student,
            another_student=another_student,
            seller=seller,
            provider=provider,
        )

    def override_db():
        with factory() as db:
            yield db

    def current_actor():
        return actors["current"]

    app.dependency_overrides[get_db] = override_db
    app.dependency_overrides[current_user] = current_actor
    client = TestClient(app)
    try:
        yield client, actors, factory
    finally:
        client.close()
        app.dependency_overrides.clear()
        Base.metadata.drop_all(engine)
        engine.dispose()


def test_student_creates_service_booking_and_provider_manages_it(request_client):
    client, actors, factory = request_client
    actors["current"] = actors["student"]

    response = client.post(
        "/service-bookings",
        json={
            "service_id": "service-1",
            "details": "Please help with calculus.",
            "requested_date": (date.today() + timedelta(days=1)).isoformat(),
        },
    )
    assert response.status_code == 201
    booking = response.json()
    assert booking["status"] == "pending"
    assert booking["role"] == "requesting"
    assert booking["counterpart"]["id"] == "provider-1"

    actors["current"] = actors["provider"]
    assert [
        row["id"] for row in client.get("/service-bookings/mine").json()
    ] == [booking["id"]]
    accepted = client.patch(
        f"/service-bookings/{booking['id']}",
        json={"status": "accepted"},
    )
    assert accepted.status_code == 200
    assert accepted.json()["status"] == "accepted"
    completed = client.patch(
        f"/service-bookings/{booking['id']}",
        json={"status": "completed"},
    )
    assert completed.status_code == 200
    assert completed.json()["status"] == "completed"

    with factory() as db:
        assert db.get(ServiceBooking, booking["id"]).status is BookingStatus.COMPLETED


def test_product_order_reserves_listing_until_completion(request_client):
    client, actors, factory = request_client
    actors["current"] = actors["student"]

    response = client.post(
        "/product-orders",
        json={"listing_id": "listing-1", "buyer_note": "Can meet after class."},
    )
    assert response.status_code == 201
    order = response.json()
    assert order["status"] == "pending"
    assert order["price"] == "25.00"
    assert order["meetup_spot"] == "Library entrance"

    with factory() as db:
        assert db.get(ProductListing, "listing-1").status is ListingStatus.RESERVED
        listing = db.get(ProductListing, "listing-1")
        listing.price = Decimal("99.00")
        listing.spot = "Different location"
        db.commit()

    actors["current"] = actors["student"]
    snapshot = client.get(f"/product-orders/{order['id']}")
    assert snapshot.status_code == 200
    assert snapshot.json()["price"] == "25.00"
    assert snapshot.json()["meetup_spot"] == "Library entrance"

    actors["current"] = actors["another_student"]
    assert client.post(
        "/product-orders", json={"listing_id": "listing-1"}
    ).status_code == 409

    actors["current"] = actors["seller"]
    accepted = client.patch(
        f"/product-orders/{order['id']}",
        json={"status": "accepted"},
    )
    assert accepted.status_code == 200
    completed = client.patch(
        f"/product-orders/{order['id']}",
        json={"status": "completed"},
    )
    assert completed.status_code == 200
    with factory() as db:
        assert db.get(ProductListing, "listing-1").status is ListingStatus.SOLD


def test_product_order_notifications_are_private_and_readable(request_client):
    client, actors, _ = request_client
    actors["current"] = actors["student"]
    created = client.post("/product-orders", json={"listing_id": "listing-1"})
    assert created.status_code == 201
    order_id = created.json()["id"]

    buyer_notifications = client.get("/notifications/mine").json()
    assert [item["notification_type"] for item in buyer_notifications] == [
        "product_order_pending"
    ]
    assert buyer_notifications[0]["href"] == f"/orders/item-{order_id}"
    assert buyer_notifications[0]["read_at"] is None
    assert client.get("/notifications/unread-count").json() == {"count": 1}

    actors["current"] = actors["seller"]
    seller_notifications = client.get("/notifications/mine").json()
    assert [item["notification_type"] for item in seller_notifications] == [
        "product_order_received"
    ]
    assert client.patch(
        f"/notifications/{buyer_notifications[0]['id']}/read"
    ).status_code == 404

    accepted = client.patch(
        f"/product-orders/{order_id}", json={"status": "accepted"}
    )
    assert accepted.status_code == 200
    actors["current"] = actors["student"]
    assert client.get("/notifications/unread-count").json() == {"count": 2}
    accepted_notification = client.patch(
        f"/notifications/{buyer_notifications[0]['id']}/read"
    )
    assert accepted_notification.status_code == 200
    assert accepted_notification.json()["read_at"] is not None
    assert client.get("/notifications/unread-count").json() == {"count": 1}

    assert client.post("/notifications/read-all").status_code == 204
    assert client.get("/notifications/unread-count").json() == {"count": 0}
    assert client.post("/notifications/read-all").status_code == 204
    actors["current"] = actors["seller"]
    assert client.get("/notifications/unread-count").json() == {"count": 1}
    completed = client.patch(
        f"/product-orders/{order_id}", json={"status": "completed"}
    )
    assert completed.status_code == 200
    actors["current"] = actors["student"]
    assert {
        item["notification_type"] for item in client.get("/notifications/mine").json()
    } == {"product_order_pending", "product_order_accepted", "product_order_completed"}
    assert client.get("/notifications/unread-count").json() == {"count": 1}


def test_declined_product_order_releases_listing_for_another_buyer(request_client):
    client, actors, _ = request_client
    actors["current"] = actors["student"]
    first = client.post("/product-orders", json={"listing_id": "listing-1"})
    assert first.status_code == 201

    actors["current"] = actors["seller"]
    declined = client.patch(
        f"/product-orders/{first.json()['id']}",
        json={"status": "declined"},
    )
    assert declined.status_code == 200

    actors["current"] = actors["student"]
    first_notifications = client.get("/notifications/mine").json()
    assert {item["notification_type"] for item in first_notifications} == {
        "product_order_pending",
        "product_order_declined",
    }
    actors["current"] = actors["another_student"]
    second = client.post("/product-orders", json={"listing_id": "listing-1"})
    assert second.status_code == 201
    assert second.json()["status"] == "pending"


def test_only_listing_seller_can_accept_and_buyer_can_cancel(request_client):
    client, actors, factory = request_client
    actors["current"] = actors["student"]
    created = client.post("/product-orders", json={"listing_id": "listing-1"})
    order_id = created.json()["id"]

    assert client.patch(
        f"/product-orders/{order_id}", json={"status": "accepted"}
    ).status_code == 409
    actors["current"] = actors["student"]
    cancelled = client.patch(
        f"/product-orders/{order_id}", json={"status": "cancelled"}
    )
    assert cancelled.status_code == 200
    assert cancelled.json()["status"] == "cancelled"
    actors["current"] = actors["seller"]
    assert {
        item["notification_type"] for item in client.get("/notifications/mine").json()
    } == {"product_order_received", "product_order_cancelled"}
    with factory() as db:
        assert db.get(ProductListing, "listing-1").status is ListingStatus.ACTIVE


def test_booking_rejects_past_dates_and_self_booking(request_client):
    client, actors, _ = request_client
    actors["current"] = actors["student"]
    past = client.post(
        "/service-bookings",
        json={
            "service_id": "service-1",
            "details": "Past date",
            "requested_date": (date.today() - timedelta(days=1)).isoformat(),
        },
    )
    assert past.status_code == 422

    own_booking = client.post(
        "/service-bookings",
        json={
            "service_id": "service-2",
            "details": "My own service",
            "requested_date": (date.today() + timedelta(days=1)).isoformat(),
        },
    )
    assert own_booking.status_code == 409

    actors["current"] = actors["provider"]
    own_booking = client.post(
        "/service-bookings",
        json={
            "service_id": "service-1",
            "details": "My own service",
            "requested_date": (date.today() + timedelta(days=1)).isoformat(),
        },
    )
    assert own_booking.status_code == 403
