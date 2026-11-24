from datetime import date, datetime, timezone
from types import SimpleNamespace
from zoneinfo import ZoneInfo

import pytest
from fastapi import HTTPException

from app.meal_locations import MEAL_PICKUP_LOCATIONS
from app.models.base import MealSession, UserRole
from app.routers.meals import _ensure_ordering_open, update_provider_contact
from app.schemas import ContactDetailsUpdate, MealProviderOut

KUALA_LUMPUR = ZoneInfo("Asia/Kuala_Lumpur")


@pytest.mark.parametrize(
    ("session", "before_cutoff", "at_cutoff"),
    [
        (
            MealSession.LUNCH,
            datetime(2026, 11, 18, 10, 29, tzinfo=KUALA_LUMPUR),
            datetime(2026, 11, 18, 10, 30, tzinfo=KUALA_LUMPUR),
        ),
        (
            MealSession.DINNER,
            datetime(2026, 11, 18, 16, 29, tzinfo=KUALA_LUMPUR),
            datetime(2026, 11, 18, 16, 30, tzinfo=KUALA_LUMPUR),
        ),
    ],
)
def test_same_day_meal_order_cutoffs(session, before_cutoff, at_cutoff):
    assert _ensure_ordering_open(session, before_cutoff) == date(2026, 11, 18)
    with pytest.raises(HTTPException) as error:
        _ensure_ordering_open(session, at_cutoff)
    assert error.value.status_code == 409


def test_cutoff_uses_kuala_lumpur_local_time():
    utc_time = datetime(2026, 11, 18, 2, 30, tzinfo=timezone.utc)
    with pytest.raises(HTTPException) as error:
        _ensure_ordering_open(MealSession.LUNCH, utc_time)
    assert error.value.status_code == 409
    assert len(MEAL_PICKUP_LOCATIONS) == len(set(MEAL_PICKUP_LOCATIONS))


def test_provider_staff_can_update_public_business_contacts():
    provider = SimpleNamespace(
        id="provider-1",
        name="Campus Cafe",
        image=None,
        whatsapp=None,
        telegram_username=None,
    )

    class Session:
        committed = False

        def scalars(self, _statement):
            return ["provider-1"]

        def get(self, _model, _provider_id):
            return provider

        def commit(self):
            self.committed = True

        def refresh(self, _value):
            pass

    session = Session()
    user = SimpleNamespace(
        id="staff-1",
        role=UserRole.FOOD_SELLER,
        is_active=True,
    )

    result = update_provider_contact(
        ContactDetailsUpdate(
            whatsapp="+60 12 345 6789",
            telegram_username="@campuscafe",
        ),
        user,
        session,
    )

    assert session.committed
    assert result.whatsapp == "+60 12 345 6789"
    assert result.telegram_username == "campuscafe"
    assert MealProviderOut.model_validate(provider).model_dump() == {
        "id": "provider-1",
        "name": "Campus Cafe",
        "image": None,
        "whatsapp": "+60 12 345 6789",
        "telegram_username": "campuscafe",
    }
