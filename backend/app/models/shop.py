from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, created_ts, str_pk
from app.models.user import User


class Shop(Base):
    """A student-run enterprise's profile page (for example a dessert stall).

    It is informational only: there is no ordering. Item listings and services
    can optionally belong to a shop. Each student can own at most one shop.
    """

    __tablename__ = "shops"

    id: Mapped[str_pk]
    owner_id: Mapped[str] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), unique=True
    )
    name: Mapped[str] = mapped_column(String(150))
    description: Mapped[str] = mapped_column(Text, default="")
    logo: Mapped[str | None] = mapped_column(String(500))
    location: Mapped[str] = mapped_column(String(200))  # free text
    hours: Mapped[str | None] = mapped_column(String(200))  # free text
    created_at: Mapped[created_ts]

    owner: Mapped[User] = relationship()
