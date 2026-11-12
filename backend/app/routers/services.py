from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.db import get_db
from app.models import Service
from app.models.base import ServiceCategory
from app.schemas import ServiceOut

router = APIRouter(prefix="/services", tags=["services"])


@router.get("", response_model=list[ServiceOut])
def list_services(
    db: Annotated[Session, Depends(get_db)],
    category: ServiceCategory | None = None,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    offset: Annotated[int, Query(ge=0)] = 0,
):
    stmt = select(Service).options(joinedload(Service.provider))
    if category:
        stmt = stmt.where(Service.category == category)
    stmt = stmt.order_by(Service.category, Service.title).limit(limit).offset(offset)
    return db.scalars(stmt).all()
