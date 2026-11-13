"""Ownership checks shared by the routes that create listings and services."""

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app import storage
from app.models import Shop, User


def check_image_key(image: str | None, user: User) -> None:
    """A new listing may only use a photo the caller uploaded themselves."""
    if image is not None and not storage.key_belongs_to(image, user.id):
        raise HTTPException(422, "image must be a key returned by POST /uploads/images")


def check_shop(db: Session, shop_id: str | None, user: User) -> None:
    """A listing may only be attached to the caller's own shop."""
    if shop_id is None:
        return
    shop = db.get(Shop, shop_id)
    if shop is None:
        raise HTTPException(404, "Shop not found")
    if shop.owner_id != user.id:
        raise HTTPException(403, "You can only list under your own shop")
