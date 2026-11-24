from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import delete, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.auth import CurrentUser
from app.db import get_db
from app.models import FoodProvider, FoodProviderStaff, Shop
from app.models.base import UserRole
from app.schemas import ContactDetailsUpdate, MeOut, RegistrationUpdate

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
        "phone": user.phone,
        "telegram_username": user.telegram_username,
        "role": user.role,
        "shop": shop,
    }


@router.patch("/contact", response_model=MeOut)
def update_contact_details(
    payload: ContactDetailsUpdate,
    user: CurrentUser,
    db: Annotated[Session, Depends(get_db)],
):
    """Update the signed-in user's public WhatsApp and Telegram contacts."""
    contact_fields = payload.model_dump(exclude_unset=True)
    if "whatsapp" in contact_fields:
        user.phone = contact_fields["whatsapp"]
    if "telegram_username" in contact_fields:
        user.telegram_username = contact_fields["telegram_username"]
    db.commit()
    db.refresh(user)
    shop = db.scalars(select(Shop).where(Shop.owner_id == user.id)).first()
    return {
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "image": user.image,
        "faculty": user.faculty,
        "phone": user.phone,
        "telegram_username": user.telegram_username,
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
        if registration.food_provider_id is not None:
            raise HTTPException(422, "Student accounts cannot be assigned to a food provider")
        if registration.student_id is None:
            raise HTTPException(422, "A matric number is required for student accounts")
        if not user.email.lower().endswith("@graduate.utm.my"):
            raise HTTPException(403, "Students must use their @graduate.utm.my email")
        user.student_id = registration.student_id
        user.role = UserRole.STUDENT
        db.execute(delete(FoodProviderStaff).where(FoodProviderStaff.user_id == user.id))
    elif registration.role == "service_provider":
        if registration.food_provider_id is not None:
            raise HTTPException(422, "Service provider accounts cannot be assigned to a food provider")
        if registration.student_id is not None:
            raise HTTPException(422, "Service provider accounts do not use a matric number")
        user.student_id = None
        user.role = UserRole.SERVICE_PROVIDER
        db.execute(delete(FoodProviderStaff).where(FoodProviderStaff.user_id == user.id))
    else:
        if registration.student_id is not None:
            raise HTTPException(422, "Food provider accounts do not use a matric number")
        if registration.food_provider_id is None:
            raise HTTPException(422, "Choose the food provider you represent")
        provider = db.get(FoodProvider, registration.food_provider_id)
        if provider is None or not provider.is_active:
            raise HTTPException(404, "Food provider not found")
        user.student_id = None
        user.role = UserRole.FOOD_SELLER
        membership = db.scalars(
            select(FoodProviderStaff).where(
                FoodProviderStaff.provider_id == provider.id,
                FoodProviderStaff.user_id == user.id,
            )
        ).first()
        if membership is None:
            db.add(FoodProviderStaff(provider_id=provider.id, user_id=user.id))

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
        "phone": user.phone,
        "telegram_username": user.telegram_username,
        "role": user.role,
        "shop": shop,
    }
