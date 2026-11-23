from types import SimpleNamespace

import pytest
from fastapi import HTTPException
from pydantic import ValidationError

from app.models.base import UserRole
from app.routers.me import update_registration
from app.schemas import RegistrationUpdate


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
