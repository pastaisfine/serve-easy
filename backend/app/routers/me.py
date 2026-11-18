from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.auth import CurrentUser
from app.db import get_db
from app.models import Shop
from app.models.base import UserRole
from app.schemas import MeOut, RegistrationUpdate

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
        "role": user.role,
        "shop": shop,
    }


@router.patch("/registration", response_model=MeOut)
def update_registration(
    registration: RegistrationUpdate,
    user: CurrentUser,
    db: Annotated[Session, Depends(get_db)],
):
    """Save the user's self-selected role and, for students, their matric number."""
    if not user.email_verified:
        raise HTTPException(403, "Verify your email before completing registration")

    if registration.role == "student":
        if registration.student_id is None:
            raise HTTPException(422, "A matric number is required for student accounts")
        if not user.email.lower().endswith("@graduate.utm.my"):
            raise HTTPException(403, "Students must use their @graduate.utm.my email")
        user.student_id = registration.student_id
        user.role = UserRole.STUDENT
    else:
        if registration.student_id is not None:
            raise HTTPException(422, "Service provider accounts do not use a matric number")
        user.student_id = None
        user.role = UserRole.SERVICE_PROVIDER

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(409, "This matric number is already registered") from None

    shop = db.scalars(select(Shop).where(Shop.owner_id == user.id)).first()
    return {
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "image": user.image,
        "faculty": user.faculty,
        "role": user.role,
        "shop": shop,
    }
