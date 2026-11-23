from sqlalchemy.orm import Session

from app.models import Notification


def create_notification(
    db: Session,
    *,
    user_id: str,
    notification_type: str,
    title: str,
    message: str,
    href: str,
    related_type: str,
    related_id: str,
) -> None:
    db.add(
        Notification(
            user_id=user_id,
            notification_type=notification_type,
            title=title,
            message=message,
            href=href,
            related_type=related_type,
            related_id=related_id,
        )
    )
