"""公告业务逻辑层。"""
from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundError
from app.models.notice import Notice
from app.models.user import User
from app.repositories import notice_repo
from app.schemas.notice import NoticeCreate


def list_notices(db: Session, limit: int | None = None) -> list[Notice]:
    return notice_repo.list_notices(db, limit)


def create_notice(db: Session, publisher: User, payload: NoticeCreate) -> Notice:
    notice = notice_repo.create(
        db,
        title=payload.title,
        content=payload.content,
        is_top=payload.is_top,
        publisher_id=publisher.id,
    )
    db.commit()
    db.refresh(notice)
    return notice


def delete_notice(db: Session, notice_id: int) -> None:
    notice = notice_repo.get_by_id(db, notice_id)
    if notice is None:
        raise NotFoundError("公告不存在")
    db.delete(notice)
    db.commit()
