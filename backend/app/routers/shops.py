from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.db import get_db
from app.models import ProductListing, Service, Shop
from app.models.base import ListingStatus
from app.schemas import ShopDetailOut, ShopOut

router = APIRouter(prefix="/shops", tags=["shops"])


@router.get("", response_model=list[ShopOut])
def list_shops(db: Annotated[Session, Depends(get_db)]):
    """Student enterprise profiles. Informational only; there is no ordering."""
    stmt = select(Shop).options(joinedload(Shop.owner)).order_by(Shop.name)
    return db.scalars(stmt).all()


@router.get("/{shop_id}", response_model=ShopDetailOut)
def get_shop(shop_id: str, db: Annotated[Session, Depends(get_db)]):
    """A shop's info plus the active listings and services that belong to it."""
    shop = db.scalar(select(Shop).options(joinedload(Shop.owner)).where(Shop.id == shop_id))
    if shop is None:
        raise HTTPException(status_code=404, detail="Shop not found")
    listings = db.scalars(
        select(ProductListing)
        .options(joinedload(ProductListing.seller), joinedload(ProductListing.shop))
        .where(ProductListing.shop_id == shop_id, ProductListing.status == ListingStatus.ACTIVE)
        .order_by(ProductListing.created_at.desc(), ProductListing.id)
    ).all()
    services = db.scalars(
        select(Service)
        .options(joinedload(Service.provider), joinedload(Service.shop))
        .where(Service.shop_id == shop_id)
        .order_by(Service.created_at.desc(), Service.id)
    ).all()
    return ShopDetailOut.model_validate(
        {
            "id": shop.id,
            "name": shop.name,
            "description": shop.description,
            "logo": shop.logo,
            "location": shop.location,
            "hours": shop.hours,
            "owner": shop.owner,
            "listings": listings,
            "services": services,
        },
        from_attributes=True,
    )
