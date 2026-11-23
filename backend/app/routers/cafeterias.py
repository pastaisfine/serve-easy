from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import FoodItem, FoodProvider
from app.models.base import MealSession
from app.schemas import CafeteriaOut, MenuOut

router = APIRouter(prefix="/cafeterias", tags=["cafeterias"])


@router.get("", response_model=list[CafeteriaOut])
def list_cafeterias(db: Annotated[Session, Depends(get_db)]):
    """Return the active providers in the integrated meal ordering section."""
    stmt = select(FoodProvider).where(FoodProvider.is_active.is_(True)).order_by(FoodProvider.name)
    return db.scalars(stmt).all()


@router.get("/{cafeteria_id}/menu", response_model=MenuOut)
def get_menu(
    cafeteria_id: str,
    db: Annotated[Session, Depends(get_db)],
    meal_session: MealSession | None = None,
):
    """Available menu items for one cafeteria, optionally for a single session."""
    cafeteria = db.get(FoodProvider, cafeteria_id)
    if cafeteria is None or not cafeteria.is_active:
        raise HTTPException(status_code=404, detail="Cafeteria not found")
    stmt = select(FoodItem).where(
        FoodItem.provider_id == cafeteria_id,
        FoodItem.available.is_(True),
    )
    if meal_session:
        stmt = stmt.where(FoodItem.meal_session == meal_session)
    stmt = stmt.order_by(FoodItem.meal_session, FoodItem.name)
    return MenuOut(cafeteria=cafeteria, items=db.scalars(stmt).all())
