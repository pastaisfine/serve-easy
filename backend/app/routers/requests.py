from datetime import datetime
from typing import Annotated
from zoneinfo import ZoneInfo

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, joinedload

from app.auth import CurrentUser
from app.db import get_db
from app.models import ProductListing, ProductOrder, Service, ServiceBooking
from app.models.base import (
    BookingStatus,
    ListingStatus,
    ProductOrderStatus,
    UserRole,
)
from app.schemas import (
    ProductOrderCreate,
    ProductOrderOut,
    ProductOrderStatusUpdate,
    ServiceBookingCreate,
    ServiceBookingOut,
    ServiceBookingStatusUpdate,
)

router = APIRouter(tags=["requests"])
_CAMPUS_TZ = ZoneInfo("Asia/Kuala_Lumpur")


def _product_order_out(order: ProductOrder, user_id: str) -> dict:
    buying = order.buyer_id == user_id
    return {
        "id": order.id,
        "listing_id": order.listing_id,
        "listing_title": order.listing_title,
        "listing_image": order.listing_image,
        "price": order.price,
        "meetup_spot": order.meetup_spot,
        "buyer_note": order.buyer_note,
        "status": order.status,
        "created_at": order.created_at,
        "role": "buying" if buying else "selling",
        "counterpart": order.seller if buying else order.buyer,
    }


def _service_booking_out(booking: ServiceBooking, user_id: str) -> dict:
    requesting = booking.student_id == user_id
    return {
        "id": booking.id,
        "service_id": booking.service_id,
        "service_title": booking.service.title,
        "service_price": booking.service.price,
        "service_unit": booking.service.unit,
        "service_spot": booking.service.spot,
        "details": booking.details,
        "requested_date": booking.requested_date,
        "status": booking.status,
        "created_at": booking.created_at,
        "role": "requesting" if requesting else "providing",
        "counterpart": booking.service.provider if requesting else booking.student,
    }


def _require_active_student(user: CurrentUser) -> None:
    if user.role is not UserRole.STUDENT or not user.is_active:
        raise HTTPException(403, "An active student account is required")


def _is_active_order_index_violation(error: IntegrityError) -> bool:
    constraint_name = getattr(getattr(error.orig, "diag", None), "constraint_name", None)
    if constraint_name == "uq_product_orders_active_listing":
        return True
    return "uq_product_orders_active_listing" in str(error.orig) or (
        "UNIQUE constraint failed: product_orders.listing_id" in str(error.orig)
    )


def _load_product_order(order_id: str, db: Session) -> ProductOrder:
    order = db.scalar(
        select(ProductOrder)
        .where(ProductOrder.id == order_id)
        .options(joinedload(ProductOrder.buyer), joinedload(ProductOrder.seller))
        .with_for_update(of=ProductOrder)
    )
    if order is None:
        raise HTTPException(404, "Product order not found")
    return order


def _load_service_booking(booking_id: str, db: Session) -> ServiceBooking:
    booking = db.scalar(
        select(ServiceBooking)
        .where(ServiceBooking.id == booking_id)
        .options(
            joinedload(ServiceBooking.student),
            joinedload(ServiceBooking.service).joinedload(Service.provider),
        )
        .with_for_update(of=ServiceBooking)
    )
    if booking is None:
        raise HTTPException(404, "Service booking not found")
    return booking


@router.post("/product-orders", response_model=ProductOrderOut, status_code=201)
def create_product_order(
    payload: ProductOrderCreate,
    user: CurrentUser,
    db: Annotated[Session, Depends(get_db)],
):
    _require_active_student(user)
    listing = db.scalar(
        select(ProductListing)
        .where(ProductListing.id == payload.listing_id)
        .with_for_update()
    )
    if listing is None or listing.status is ListingStatus.REMOVED:
        raise HTTPException(404, "Listing not found")
    if listing.status is not ListingStatus.ACTIVE:
        raise HTTPException(409, "This listing is not available to order")
    if listing.seller_id == user.id:
        raise HTTPException(409, "You cannot order your own listing")

    order = ProductOrder(
        listing_id=listing.id,
        buyer_id=user.id,
        seller_id=listing.seller_id,
        listing_title=listing.title,
        listing_image=listing.image,
        price=listing.price,
        meetup_spot=listing.spot,
        buyer_note=payload.buyer_note or None,
        status=ProductOrderStatus.PENDING,
    )
    listing.status = ListingStatus.RESERVED
    db.add(order)
    try:
        db.commit()
    except IntegrityError as error:
        db.rollback()
        if not _is_active_order_index_violation(error):
            raise
        raise HTTPException(409, "This listing already has an active order request") from None
    db.refresh(order)
    db.refresh(order.buyer)
    db.refresh(order.seller)
    return _product_order_out(order, user.id)


@router.get("/product-orders/mine", response_model=list[ProductOrderOut])
def list_my_product_orders(
    user: CurrentUser,
    db: Annotated[Session, Depends(get_db)],
    limit: Annotated[int, Query(ge=1, le=100)] = 100,
):
    orders = db.scalars(
        select(ProductOrder)
        .where(or_(ProductOrder.buyer_id == user.id, ProductOrder.seller_id == user.id))
        .options(joinedload(ProductOrder.buyer), joinedload(ProductOrder.seller))
        .order_by(ProductOrder.created_at.desc(), ProductOrder.id)
        .limit(limit)
    ).all()
    return [_product_order_out(order, user.id) for order in orders]


@router.get("/product-orders/{order_id}", response_model=ProductOrderOut)
def get_my_product_order(
    order_id: str,
    user: CurrentUser,
    db: Annotated[Session, Depends(get_db)],
):
    order = db.scalar(
        select(ProductOrder)
        .where(
            ProductOrder.id == order_id,
            or_(ProductOrder.buyer_id == user.id, ProductOrder.seller_id == user.id),
        )
        .options(joinedload(ProductOrder.buyer), joinedload(ProductOrder.seller))
    )
    if order is None:
        raise HTTPException(404, "Product order not found")
    return _product_order_out(order, user.id)


@router.patch("/product-orders/{order_id}", response_model=ProductOrderOut)
def update_product_order(
    order_id: str,
    payload: ProductOrderStatusUpdate,
    user: CurrentUser,
    db: Annotated[Session, Depends(get_db)],
):
    order = _load_product_order(order_id, db)
    is_buyer = order.buyer_id == user.id
    is_seller = order.seller_id == user.id
    if not is_buyer and not is_seller:
        raise HTTPException(404, "Product order not found")

    if is_buyer:
        allowed = (
            {ProductOrderStatus.CANCELLED}
            if order.status in {ProductOrderStatus.PENDING, ProductOrderStatus.ACCEPTED}
            else set()
        )
    elif order.status is ProductOrderStatus.PENDING:
        allowed = {ProductOrderStatus.ACCEPTED, ProductOrderStatus.DECLINED}
    elif order.status is ProductOrderStatus.ACCEPTED:
        allowed = {ProductOrderStatus.COMPLETED}
    else:
        allowed = set()
    if payload.status not in allowed:
        raise HTTPException(409, "This product order cannot move to that status")

    listing = db.scalar(
        select(ProductListing)
        .where(ProductListing.id == order.listing_id)
        .with_for_update()
    )
    if listing is None:
        raise HTTPException(409, "The listing for this order no longer exists")
    order.status = payload.status
    if payload.status is ProductOrderStatus.COMPLETED:
        listing.status = ListingStatus.SOLD
    elif payload.status in {ProductOrderStatus.DECLINED, ProductOrderStatus.CANCELLED}:
        listing.status = ListingStatus.ACTIVE

    db.commit()
    db.refresh(order)
    return _product_order_out(order, user.id)


@router.post("/service-bookings", response_model=ServiceBookingOut, status_code=201)
def create_service_booking(
    payload: ServiceBookingCreate,
    user: CurrentUser,
    db: Annotated[Session, Depends(get_db)],
):
    _require_active_student(user)
    today = datetime.now(_CAMPUS_TZ).date()
    if payload.requested_date < today:
        raise HTTPException(422, "Choose today or a future date")

    service = db.get(Service, payload.service_id)
    if service is None:
        raise HTTPException(404, "Service not found")
    if service.provider_id == user.id:
        raise HTTPException(409, "You cannot book your own service")

    booking = ServiceBooking(
        student_id=user.id,
        service_id=service.id,
        details=payload.details,
        requested_date=payload.requested_date,
        status=BookingStatus.PENDING,
    )
    db.add(booking)
    db.commit()
    db.refresh(booking)
    booking.student = user
    booking.service = service
    return _service_booking_out(booking, user.id)


@router.get("/service-bookings/mine", response_model=list[ServiceBookingOut])
def list_my_service_bookings(
    user: CurrentUser,
    db: Annotated[Session, Depends(get_db)],
    limit: Annotated[int, Query(ge=1, le=100)] = 100,
):
    bookings = db.scalars(
        select(ServiceBooking)
        .join(Service)
        .where(or_(ServiceBooking.student_id == user.id, Service.provider_id == user.id))
        .options(
            joinedload(ServiceBooking.student),
            joinedload(ServiceBooking.service).joinedload(Service.provider),
        )
        .order_by(ServiceBooking.created_at.desc(), ServiceBooking.id)
        .limit(limit)
    ).all()
    return [_service_booking_out(booking, user.id) for booking in bookings]


@router.get("/service-bookings/{booking_id}", response_model=ServiceBookingOut)
def get_my_service_booking(
    booking_id: str,
    user: CurrentUser,
    db: Annotated[Session, Depends(get_db)],
):
    booking = db.scalar(
        select(ServiceBooking)
        .join(Service)
        .where(
            ServiceBooking.id == booking_id,
            or_(ServiceBooking.student_id == user.id, Service.provider_id == user.id),
        )
        .options(
            joinedload(ServiceBooking.student),
            joinedload(ServiceBooking.service).joinedload(Service.provider),
        )
    )
    if booking is None:
        raise HTTPException(404, "Service booking not found")
    return _service_booking_out(booking, user.id)


@router.patch("/service-bookings/{booking_id}", response_model=ServiceBookingOut)
def update_service_booking(
    booking_id: str,
    payload: ServiceBookingStatusUpdate,
    user: CurrentUser,
    db: Annotated[Session, Depends(get_db)],
):
    booking = _load_service_booking(booking_id, db)
    is_student = booking.student_id == user.id
    is_provider = booking.service.provider_id == user.id
    if not is_student and not is_provider:
        raise HTTPException(404, "Service booking not found")

    if is_student:
        allowed = (
            {BookingStatus.CANCELLED}
            if booking.status in {BookingStatus.PENDING, BookingStatus.ACCEPTED}
            else set()
        )
    elif booking.status is BookingStatus.PENDING:
        allowed = {BookingStatus.ACCEPTED, BookingStatus.DECLINED}
    elif booking.status is BookingStatus.ACCEPTED:
        allowed = {BookingStatus.COMPLETED}
    else:
        allowed = set()
    if payload.status not in allowed:
        raise HTTPException(409, "This service booking cannot move to that status")

    booking.status = payload.status
    db.commit()
    db.refresh(booking)
    return _service_booking_out(booking, user.id)
