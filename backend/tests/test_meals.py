from datetime import date, datetime, timezone
from zoneinfo import ZoneInfo

import pytest
from fastapi import HTTPException

from app.meal_locations import MEAL_PICKUP_LOCATIONS
from app.models.base import MealSession
from app.routers.meals import _ensure_ordering_open

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
