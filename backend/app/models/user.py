from datetime import datetime

from sqlalchemy import Boolean, DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, UserRole, created_ts, pg_enum, str_pk


class User(Base):
    """Shared account entity for students, food sellers and service providers.

    Field names mirror Better Auth's core user table (id, name, email,
    email_verified, image, created_at, updated_at) so auth can be added later
    with a field mapping. There is intentionally no password column yet.
    """

    __tablename__ = "users"

    id: Mapped[str_pk]
    name: Mapped[str] = mapped_column(String(120))
    email: Mapped[str] = mapped_column(String(255), unique=True)
    email_verified: Mapped[bool] = mapped_column(Boolean, default=False, server_default="false")
    image: Mapped[str | None] = mapped_column(String(500))
    student_id: Mapped[str | None] = mapped_column(String(32), unique=True)
    role: Mapped[UserRole] = mapped_column(pg_enum(UserRole, "user_role"), default=UserRole.STUDENT)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, server_default="true")
    phone: Mapped[str | None] = mapped_column(String(32))
    faculty: Mapped[str | None] = mapped_column(String(120))
    created_at: Mapped[created_ts]
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
