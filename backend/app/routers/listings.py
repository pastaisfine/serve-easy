from decimal import Decimal
from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.db import get_db
from app.models import ProductListing
from app.models.base import ListingCategory, ListingCondition, ListingStatus
from app.schemas import ListingOut

router = APIRouter(prefix="/listings", tags=["listings"])


@router.get("", response_model=list[ListingOut])
def list_listings(
    db: Annotated[Session, Depends(get_db)],
    category: ListingCategory | None = None,
    condition: ListingCondition | None = None,
    min_price: Annotated[Decimal | None, Query(ge=0)] = None,
    max_price: Annotated[Decimal | None, Query(ge=0)] = None,
    q: Annotated[str | None, Query(min_length=1, max_length=100, description="Search in the title")] = None,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    offset: Annotated[int, Query(ge=0)] = 0,
):
    """Active listings, newest first."""
    stmt = (
        select(ProductListing)
        .options(joinedload(ProductListing.seller), joinedload(ProductListing.shop))
        .where(ProductListing.status == ListingStatus.ACTIVE)
    )
    if category:
        stmt = stmt.where(ProductListing.category == category)
    if condition:
        stmt = stmt.where(ProductListing.condition == condition)
    if min_price is not None:
        stmt = stmt.where(ProductListing.price >= min_price)
    if max_price is not None:
        stmt = stmt.where(ProductListing.price <= max_price)
    if q:
        escaped = q.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
        stmt = stmt.where(ProductListing.title.ilike(f"%{escaped}%", escape="\\"))
    stmt = stmt.order_by(ProductListing.created_at.desc(), ProductListing.id).limit(limit).offset(offset)
    return db.scalars(stmt).all()
