from collections import defaultdict
from datetime import UTC, date, datetime, time
from decimal import Decimal
from typing import Annotated
from uuid import uuid4
from zoneinfo import ZoneInfo

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, update
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session, selectinload

from app import storage
from app.auth import CurrentUser
from app.db import get_db
from app.meal_locations import MEAL_PICKUP_LOCATIONS
from app.models import (
    FoodDeliveryBatch,
    FoodItem,
    FoodOrder,
    FoodProvider,
    FoodProviderStaff,
    OrderLineItem,
)
from app.models.base import DeliveryStatus, MealSession, OrderStatus, UserRole
from app.schemas import (
    ContactDetailsUpdate,
    FoodItemOut,
    MealDeliveryBatchOut,
    MealDeliveryBatchUpdate,
    MealMenuItemCreate,
    MealMenuItemUpdate,
    MealOrderCreate,
    MealOrderList,
    MealOrderOut,
    MealProviderOut,
    ProviderDeliveryBatchOut,
)

router = APIRouter(prefix="/meals", tags=["meals"])
_CAMPUS_TZ = ZoneInfo("Asia/Kuala_Lumpur")
_CUTOFFS = {MealSession.LUNCH: time(10, 30), MealSession.DINNER: time(16, 30)}


def _local_now() -> datetime:
    return datetime.now(_CAMPUS_TZ)


def _ensure_ordering_open(session: MealSession, now: datetime | None = None) -> date:
    local_now = now.astimezone(_CAMPUS_TZ) if now else _local_now()
    if local_now.time() >= _CUTOFFS[session]:
        label = "10:30" if session is MealSession.LUNCH else "16:30"
        raise HTTPException(409, f"{session.value.title()} ordering closed at {label}")
    return local_now.date()


def _provider_ids_for_staff(db: Session, user_id: str) -> list[str]:
    result = db.scalars(
        select(FoodProviderStaff.provider_id)
        .join(FoodProvider)
        .where(
            FoodProviderStaff.user_id == user_id,
            FoodProvider.is_active.is_(True),
        )
    )
    return list(result)


def _require_provider_staff(user: CurrentUser, db: Session) -> list[str]:
    if user.role is not UserRole.FOOD_SELLER or not user.is_active:
        raise HTTPException(403, "Food provider staff access required")
    provider_ids = _provider_ids_for_staff(db, user.id)
    if not provider_ids:
        raise HTTPException(403, "This account is not assigned to an active food provider")
    return provider_ids


@router.get("/provider", response_model=MealProviderOut)
def get_my_provider(user: CurrentUser, db: Annotated[Session, Depends(get_db)]):
    provider_ids = _require_provider_staff(user, db)
    provider = db.get(FoodProvider, provider_ids[0])
    if provider is None:
        raise HTTPException(404, "Food provider not found")
    return provider


@router.patch("/provider/contact", response_model=MealProviderOut)
def update_provider_contact(
    payload: ContactDetailsUpdate,
    user: CurrentUser,
    db: Annotated[Session, Depends(get_db)],
):
    """Update public contact details for the staff member's active provider."""
    provider_ids = _require_provider_staff(user, db)
    provider = db.get(FoodProvider, provider_ids[0])
    if provider is None:
        raise HTTPException(404, "Food provider not found")
    contact_fields = payload.model_dump(exclude_unset=True)
    for field, value in contact_fields.items():
        setattr(provider, field, value)
    db.commit()
    db.refresh(provider)
    return provider


@router.get("/provider/menu", response_model=list[FoodItemOut])
def list_provider_menu(user: CurrentUser, db: Annotated[Session, Depends(get_db)]):
    provider_ids = _require_provider_staff(user, db)
    stmt = (
        select(FoodItem)
        .where(FoodItem.provider_id == provider_ids[0])
        .order_by(FoodItem.meal_session, FoodItem.name)
    )
    return db.scalars(stmt).all()


@router.get("/locations", response_model=list[str])
def list_pickup_locations():
    return list(MEAL_PICKUP_LOCATIONS)


@router.get("/batches", response_model=list[MealDeliveryBatchOut])
def list_delivery_batches(
    user: CurrentUser,
    db: Annotated[Session, Depends(get_db)],
    meal_session: MealSession,
    delivery_date: date | None = None,
):
    day = delivery_date or _local_now().date()
    stmt = (
        select(FoodDeliveryBatch)
        .join(FoodProvider)
        .where(
            FoodDeliveryBatch.meal_session == meal_session,
            FoodDeliveryBatch.delivery_date == day,
            FoodProvider.is_active.is_(True),
        )
        .options(selectinload(FoodDeliveryBatch.provider))
        .order_by(FoodDeliveryBatch.pickup_location, FoodProvider.name)
    )
    return db.scalars(stmt).all()


@router.post("/orders", response_model=MealOrderList, status_code=201)
def create_meal_orders(
    payload: MealOrderCreate,
    user: CurrentUser,
    db: Annotated[Session, Depends(get_db)],
):
    if user.role is not UserRole.STUDENT or not user.is_active:
        raise HTTPException(403, "Student account required to place a meal order")
    if payload.pickup_location not in MEAL_PICKUP_LOCATIONS:
        raise HTTPException(422, "Choose a pickup point from the campus list")
    delivery_date = _ensure_ordering_open(payload.meal_session)

    item_ids = [line.item_id for line in payload.items]
    if len(set(item_ids)) != len(item_ids):
        raise HTTPException(422, "Each menu item can appear only once in the cart")
    items = db.scalars(
        select(FoodItem)
        .where(FoodItem.id.in_(item_ids))
        .with_for_update()
    ).all()
    if len(items) != len(item_ids):
        raise HTTPException(409, "One or more menu items are no longer available")

    quantities = {line.item_id: line.quantity for line in payload.items}
    grouped: dict[str, list[FoodItem]] = defaultdict(list)
    for item in items:
        if (
            not item.available
            or item.meal_session is not payload.meal_session
            or item.provider_id is None
            or item.provider is None
            or not item.provider.is_active
        ):
            raise HTTPException(409, f"{item.name} is no longer available for this meal")
        grouped[item.provider_id].append(item)

    order_ids: list[str] = []
    for provider_id, provider_items in grouped.items():
        db.execute(
            insert(FoodDeliveryBatch)
            .values(
                id=str(uuid4()),
                provider_id=provider_id,
                meal_session=payload.meal_session,
                delivery_date=delivery_date,
                pickup_location=payload.pickup_location,
                status=DeliveryStatus.PREPARING,
            )
            .on_conflict_do_nothing(constraint="uq_food_delivery_batch_scope")
        )
        batch = db.scalar(
            select(FoodDeliveryBatch).where(
                FoodDeliveryBatch.provider_id == provider_id,
                FoodDeliveryBatch.meal_session == payload.meal_session,
                FoodDeliveryBatch.delivery_date == delivery_date,
                FoodDeliveryBatch.pickup_location == payload.pickup_location,
            )
        )
        if batch is None:
            raise HTTPException(500, "Could not create the delivery batch")

        total = sum(
            (item.price * quantities[item.id] for item in provider_items),
            Decimal("0.00"),
        )
        order = FoodOrder(
            buyer_id=user.id,
            seller_id=None,
            provider_id=provider_id,
            delivery_batch_id=batch.id,
            total=total,
            status=OrderStatus.CONFIRMED,
        )
        order.lines = [
            OrderLineItem(
                item_id=item.id,
                item_name=item.name,
                quantity=quantities[item.id],
                unit_price=item.price,
            )
            for item in provider_items
        ]
        db.add(order)
        db.flush()
        order_ids.append(order.id)

    db.commit()
    stmt = (
        select(FoodOrder)
        .where(FoodOrder.id.in_(order_ids))
        .options(
            selectinload(FoodOrder.provider),
            selectinload(FoodOrder.delivery_batch).selectinload(FoodDeliveryBatch.provider),
            selectinload(FoodOrder.lines).selectinload(OrderLineItem.item),
        )
        .order_by(FoodOrder.created_at)
    )
    return MealOrderList(orders=db.scalars(stmt).all())


@router.get("/orders/mine", response_model=MealOrderList)
def list_my_meal_orders(user: CurrentUser, db: Annotated[Session, Depends(get_db)]):
    stmt = (
        select(FoodOrder)
        .where(FoodOrder.buyer_id == user.id, FoodOrder.provider_id.is_not(None))
        .options(
            selectinload(FoodOrder.provider),
            selectinload(FoodOrder.delivery_batch).selectinload(FoodDeliveryBatch.provider),
            selectinload(FoodOrder.lines).selectinload(OrderLineItem.item),
        )
        .order_by(FoodOrder.created_at.desc())
    )
    return MealOrderList(orders=db.scalars(stmt).all())


@router.get("/provider/orders", response_model=list[ProviderDeliveryBatchOut])
def list_provider_orders(
    user: CurrentUser,
    db: Annotated[Session, Depends(get_db)],
    meal_session: MealSession | None = None,
    delivery_date: date | None = None,
):
    provider_ids = _require_provider_staff(user, db)
    stmt = (
        select(FoodDeliveryBatch)
        .where(FoodDeliveryBatch.provider_id.in_(provider_ids))
        .options(
            selectinload(FoodDeliveryBatch.provider),
            selectinload(FoodDeliveryBatch.orders)
            .selectinload(FoodOrder.buyer),
            selectinload(FoodDeliveryBatch.orders)
            .selectinload(FoodOrder.lines)
            .selectinload(OrderLineItem.item),
        )
        .order_by(FoodDeliveryBatch.delivery_date.desc(), FoodDeliveryBatch.pickup_location)
    )
    if meal_session:
        stmt = stmt.where(FoodDeliveryBatch.meal_session == meal_session)
    if delivery_date:
        stmt = stmt.where(FoodDeliveryBatch.delivery_date == delivery_date)
    return db.scalars(stmt).all()


@router.post("/provider/menu", response_model=FoodItemOut, status_code=201)
def create_menu_item(
    payload: MealMenuItemCreate,
    user: CurrentUser,
    db: Annotated[Session, Depends(get_db)],
):
    provider_ids = _require_provider_staff(user, db)
    if payload.image and not storage.key_belongs_to(payload.image, user.id, namespace="meals"):
        raise HTTPException(422, "Menu photos must be uploaded by this account")
    item = FoodItem(
        seller_id=user.id,
        provider_id=provider_ids[0],
        name=payload.name,
        price=payload.price,
        meal_session=payload.meal_session,
        image=payload.image,
        available=True,
        is_demo=False,
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.patch("/provider/menu/{item_id}", response_model=FoodItemOut)
def update_menu_item(
    item_id: str,
    payload: MealMenuItemUpdate,
    user: CurrentUser,
    db: Annotated[Session, Depends(get_db)],
):
    provider_ids = _require_provider_staff(user, db)
    item = db.get(FoodItem, item_id)
    if item is None or item.provider_id not in provider_ids:
        raise HTTPException(404, "Menu item not found")
    if payload.image and not storage.key_belongs_to(payload.image, user.id, namespace="meals"):
        raise HTTPException(422, "Menu photos must be uploaded by this account")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(item, field, value)
    db.commit()
    db.refresh(item)
    return item


@router.patch("/provider/batches/{batch_id}", response_model=ProviderDeliveryBatchOut)
def update_delivery_batch(
    batch_id: str,
    payload: MealDeliveryBatchUpdate,
    user: CurrentUser,
    db: Annotated[Session, Depends(get_db)],
):
    provider_ids = _require_provider_staff(user, db)
    batch = db.scalar(
        select(FoodDeliveryBatch)
        .where(FoodDeliveryBatch.id == batch_id)
        .options(
            selectinload(FoodDeliveryBatch.provider),
            selectinload(FoodDeliveryBatch.orders)
            .selectinload(FoodOrder.buyer),
            selectinload(FoodDeliveryBatch.orders)
            .selectinload(FoodOrder.lines)
            .selectinload(OrderLineItem.item),
        )
        .with_for_update()
    )
    if batch is None or batch.provider_id not in provider_ids:
        raise HTTPException(404, "Delivery batch not found")

    allowed = {
        DeliveryStatus.PREPARING: {DeliveryStatus.ON_THE_WAY},
        DeliveryStatus.ON_THE_WAY: {DeliveryStatus.DELIVERED},
        DeliveryStatus.DELIVERED: {DeliveryStatus.DELIVERED},
    }
    if payload.status is not batch.status and payload.status not in allowed[batch.status]:
        raise HTTPException(409, "Delivery batches must move from preparing to on the way to delivered")
    if payload.status is DeliveryStatus.DELIVERED:
        if not payload.proof_image:
            raise HTTPException(422, "Upload a delivery photo before marking this batch delivered")
        if not storage.key_belongs_to(payload.proof_image, user.id, namespace="meals"):
            raise HTTPException(422, "Delivery photos must be uploaded by this account")
        batch.proof_image = payload.proof_image
        if batch.delivered_at is None:
            batch.delivered_at = datetime.now(UTC)

    batch.status = payload.status
    order_status = (
        OrderStatus.READY
        if payload.status is DeliveryStatus.ON_THE_WAY
        else OrderStatus.COMPLETED
        if payload.status is DeliveryStatus.DELIVERED
        else None
    )
    if order_status is not None:
        db.execute(
            update(FoodOrder)
            .where(FoodOrder.delivery_batch_id == batch.id)
            .values(status=order_status)
        )
    db.commit()
    updated = db.scalar(
        select(FoodDeliveryBatch)
        .where(FoodDeliveryBatch.id == batch.id)
        .options(
            selectinload(FoodDeliveryBatch.provider),
            selectinload(FoodDeliveryBatch.orders)
            .selectinload(FoodOrder.buyer),
            selectinload(FoodDeliveryBatch.orders)
            .selectinload(FoodOrder.lines)
            .selectinload(OrderLineItem.item),
        )
    )
    if updated is None:
        raise HTTPException(500, "Could not reload the updated delivery batch")
    return updated
