from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import FoodItem, User
from app.models.base import MealSession, UserRole
from app.schemas import CafeteriaOut, MenuOut

router = APIRouter(prefix="/cafeterias", tags=["cafeterias"])


@router.get("", response_model=list[CafeteriaOut])
def list_cafeterias(db: Annotated[Session, Depends(get_db)]):
    """A cafeteria is a user with the food_seller role."""
    stmt = select(User).where(User.role == UserRole.FOOD_SELLER).order_by(User.name)
    return db.scalars(stmt).all()


@router.get("/{cafeteria_id}/menu", response_model=MenuOut)
def get_menu(
    cafeteria_id: str,
    db: Annotated[Session, Depends(get_db)],
    meal_session: MealSession | None = None,
):
    """Available menu items for one cafeteria, optionally for a single session."""
    cafeteria = db.get(User, cafeteria_id)
    if cafeteria is None or cafeteria.role != UserRole.FOOD_SELLER:
        raise HTTPException(status_code=404, detail="Cafeteria not found")
    stmt = select(FoodItem).where(FoodItem.seller_id == cafeteria_id, FoodItem.available.is_(True))
    if meal_session:
        stmt = stmt.where(FoodItem.meal_session == meal_session)
    stmt = stmt.order_by(FoodItem.meal_session, FoodItem.name)
    return MenuOut(cafeteria=cafeteria, items=db.scalars(stmt).all())
