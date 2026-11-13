from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth import CurrentUser
from app.db import get_db
from app.models import Shop
from app.schemas import MeOut

router = APIRouter(prefix="/me", tags=["me"])


@router.get("", response_model=MeOut)
def read_me(user: CurrentUser, db: Annotated[Session, Depends(get_db)]):
    """The signed-in user and their shop, if they have one."""
    shop = db.scalars(select(Shop).where(Shop.owner_id == user.id)).first()
    return {
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "image": user.image,
        "faculty": user.faculty,
        "shop": shop,
    }
