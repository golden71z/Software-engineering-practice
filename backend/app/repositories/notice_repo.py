"""公告数据访问层。"""
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.notice import Notice


def list_notices(db: Session, limit: int | None = None) -> list[Notice]:
    stmt = select(Notice).order_by(Notice.is_top.desc(), Notice.created_at.desc())
    if limit:
        stmt = stmt.limit(limit)
    return list(db.scalars(stmt).all())


def get_by_id(db: Session, notice_id: int) -> Notice | None:
    return db.get(Notice, notice_id)


def create(db: Session, **fields) -> Notice:
    notice = Notice(**fields)
    db.add(notice)
    db.flush()
    return notice
