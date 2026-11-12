from sqlalchemy import CheckConstraint, ForeignKey, Index, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, created_ts, str_pk
from app.models.user import User


class Message(Base):
    __tablename__ = "messages"
    __table_args__ = (
        CheckConstraint("sender_id <> receiver_id", name="ck_messages_not_self"),
        Index("ix_messages_conversation", "sender_id", "receiver_id", "created_at"),
    )

    id: Mapped[str_pk]
    sender_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    receiver_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    content: Mapped[str] = mapped_column(Text)
    created_at: Mapped[created_ts]

    sender: Mapped[User] = relationship(foreign_keys=[sender_id])
    receiver: Mapped[User] = relationship(foreign_keys=[receiver_id])
