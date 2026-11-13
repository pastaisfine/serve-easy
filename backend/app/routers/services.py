from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.auth import CurrentUser
from app.db import get_db
from app.models import Service
from app.models.base import ServiceCategory
from app.routers._shared import check_image_key, check_shop
from app.schemas import ServiceCreate, ServiceOut

router = APIRouter(prefix="/services", tags=["services"])


@router.get("", response_model=list[ServiceOut])
def list_services(
    db: Annotated[Session, Depends(get_db)],
    category: ServiceCategory | None = None,
    q: Annotated[str | None, Query(min_length=1, max_length=100, description="Search in the title")] = None,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    offset: Annotated[int, Query(ge=0)] = 0,
):
    stmt = select(Service).options(joinedload(Service.provider), joinedload(Service.shop))
    if category:
        stmt = stmt.where(Service.category == category)
    if q:
        escaped = q.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
        stmt = stmt.where(Service.title.ilike(f"%{escaped}%", escape="\\"))
    stmt = stmt.order_by(Service.created_at.desc(), Service.id).limit(limit).offset(offset)
    return db.scalars(stmt).all()


@router.get("/{service_id}", response_model=ServiceOut)
def get_service(service_id: str, db: Annotated[Session, Depends(get_db)]):
    stmt = (
        select(Service)
        .options(joinedload(Service.provider), joinedload(Service.shop))
        .where(Service.id == service_id)
    )
    service = db.scalars(stmt).first()
    if service is None:
        raise HTTPException(404, "Service not found")
    return service


@router.post("", response_model=ServiceOut, status_code=201)
def create_service(
    body: ServiceCreate,
    db: Annotated[Session, Depends(get_db)],
    user: CurrentUser,
):
    """Offer a service. Any signed-in student can; it goes live immediately."""
    check_image_key(body.image, user)
    check_shop(db, body.shop_id, user)
    service = Service(provider_id=user.id, **body.model_dump())
    db.add(service)
    db.commit()
    db.refresh(service)
    return service
