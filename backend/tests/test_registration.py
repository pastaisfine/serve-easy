from types import SimpleNamespace

import pytest
from fastapi import HTTPException
from pydantic import ValidationError

from app.models.base import UserRole
from app.routers.me import update_registration
from app.routers.me import update_contact_details
from app.schemas import ContactDetailsUpdate, RegistrationUpdate, UserSummary


class FakeResult:
    def first(self):
        return None


class FakeSession:
    def __init__(self):
        self.committed = False
        self.added = []

    def commit(self):
        self.committed = True

    def rollback(self):
        pass

    def refresh(self, _value):
        pass

    def execute(self, _statement):
        pass

    def get(self, _model, provider_id):
        return SimpleNamespace(id=provider_id, is_active=True)

    def add(self, value):
        self.added.append(value)

    def scalars(self, _statement):
        return FakeResult()


def account(*, email="student@graduate.utm.my", verified=True):
    return SimpleNamespace(
        id="account-1",
        name="Serve User",
        email=email,
        email_verified=verified,
        image=None,
        faculty=None,
        role=UserRole.STUDENT,
        student_id=None,
        phone=None,
        telegram_username=None,
    )


def test_student_registration_normalizes_and_saves_matric_number():
    user = account()
    db = FakeSession()

    result = update_registration(
        RegistrationUpdate(role="student", student_id="a26kt0123"),
        user,
        db,
    )

    assert user.student_id == "A26KT0123"
    assert user.role == UserRole.STUDENT
    assert result["role"] == UserRole.STUDENT
    assert db.committed


def test_student_registration_requires_verified_utm_email():
    with pytest.raises(HTTPException) as error:
        update_registration(
            RegistrationUpdate(role="student", student_id="A26KT0123"),
            account(email="student@example.com"),
            FakeSession(),
        )

    assert error.value.status_code == 403


def test_provider_registration_needs_no_matric_number():
    user = account(email="provider@example.com")
    db = FakeSession()

    result = update_registration(
        RegistrationUpdate(role="service_provider"),
        user,
        db,
    )

    assert user.role == UserRole.SERVICE_PROVIDER
    assert user.student_id is None
    assert result["role"] == UserRole.SERVICE_PROVIDER
    assert db.committed


def test_food_staff_registration_assigns_the_selected_provider():
    from app.models import FoodProviderStaff

    user = account(email="provider@example.com")
    db = FakeSession()

    result = update_registration(
        RegistrationUpdate(role="food_seller", food_provider_id="provider-1"),
        user,
        db,
    )

    assert user.role == UserRole.FOOD_SELLER
    assert user.student_id is None
    assert result["role"] == UserRole.FOOD_SELLER
    assert len(db.added) == 1
    assert isinstance(db.added[0], FoodProviderStaff)
    assert db.added[0].provider_id == "provider-1"
    assert db.added[0].user_id == user.id
    assert db.committed


def test_registration_rejects_matric_numbers_outside_the_utm_format():
    with pytest.raises(ValidationError):
        RegistrationUpdate(role="student", student_id="A26KT123")


def test_registration_requires_email_verification_for_all_roles():
    with pytest.raises(HTTPException) as error:
        update_registration(
            RegistrationUpdate(role="service_provider"),
            account(email="provider@example.com", verified=False),
            FakeSession(),
        )

    assert error.value.status_code == 403


def test_contact_details_normalize_and_save_optional_contacts():
    user = account()
    db = FakeSession()
    payload = ContactDetailsUpdate(
        whatsapp="+60 12-345 6789",
        telegram_username="@serve_user",
    )

    result = update_contact_details(payload, user, db)

    assert user.phone == "+60 12-345 6789"
    assert user.telegram_username == "serve_user"
    assert result["phone"] == user.phone
    assert result["telegram_username"] == user.telegram_username
    assert db.committed


def test_public_user_summary_uses_public_contact_field_names():
    summary = UserSummary.model_validate(account())
    assert summary.whatsapp is None
    assert summary.telegram_username is None
    assert "phone" not in summary.model_dump()
    assert "whatsapp" in summary.model_dump()


def test_contact_details_can_be_cleared():
    user = account()
    user.phone = "+60123456789"
    user.telegram_username = "serve_user"
    db = FakeSession()

    update_contact_details(
        ContactDetailsUpdate(whatsapp=None, telegram_username=None),
        user,
        db,
    )

    assert user.phone is None
    assert user.telegram_username is None


@pytest.mark.parametrize(
    "payload",
    [
        {"whatsapp": "not a phone"},
        {"whatsapp": "0123456789"},
        {"telegram_username": "@12345"},
        {"telegram_username": "名字名字名字"},
    ],
)
def test_contact_details_reject_invalid_values(payload):
    with pytest.raises(ValidationError):
        ContactDetailsUpdate(**payload)
