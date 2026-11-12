from datetime import date

from sqlalchemy import Date, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import (
    Base,
    BookingStatus,
    ServiceCategory,
    created_ts,
    money,
    pg_enum,
    str_pk,
)
from app.models.user import User


class Service(Base):
    __tablename__ = "services"

    id: Mapped[str_pk]
    provider_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    title: Mapped[str] = mapped_column(String(200))
    description: Mapped[str] = mapped_column(Text, default="")
    price: Mapped[money]
    category: Mapped[ServiceCategory] = mapped_column(pg_enum(ServiceCategory, "service_category"))

    provider: Mapped[User] = relationship()


class ServiceBooking(Base):
    __tablename__ = "service_bookings"

    id: Mapped[str_pk]
    student_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    service_id: Mapped[str] = mapped_column(ForeignKey("services.id", ondelete="CASCADE"), index=True)
    details: Mapped[str] = mapped_column(Text)
    requested_date: Mapped[date] = mapped_column(Date)
    status: Mapped[BookingStatus] = mapped_column(
        pg_enum(BookingStatus, "booking_status"), default=BookingStatus.PENDING
    )
    created_at: Mapped[created_ts]

    student: Mapped[User] = relationship()
    service: Mapped[Service] = relationship()
