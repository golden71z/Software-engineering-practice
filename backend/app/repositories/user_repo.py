"""用户数据访问层。

这一层只负责"怎么取数据、怎么存数据"，不判断任何业务规则。
对应 Java 里的 Mapper。换数据库或加缓存时，只改这里。
"""
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.user import User


def get_by_id(db: Session, user_id: int) -> User | None:
    return db.get(User, user_id)


def get_by_username(db: Session, username: str) -> User | None:
    return db.scalar(select(User).where(User.username == username))


def get_by_email(db: Session, email: str) -> User | None:
    return db.scalar(select(User).where(User.email == email))


def exists_username(db: Session, username: str) -> bool:
    return db.scalar(select(User.id).where(User.username == username)) is not None


def exists_email(db: Session, email: str) -> bool:
    return db.scalar(select(User.id).where(User.email == email)) is not None


def create(db: Session, **fields) -> User:
    """新建用户并 flush（拿到自增 ID），提交事务由 service 层决定。"""
    user = User(**fields)
    db.add(user)
    db.flush()
    return user


def search(
    db: Session,
    *,
    keyword: str | None = None,
    role: str | None = None,
    page: int = 1,
    size: int = 10,
) -> tuple[list[User], int]:
    """管理端用户列表：支持按用户名/姓名/邮箱模糊搜，可按角色过滤。"""
    from sqlalchemy import func, or_

    stmt = select(User)
    if keyword:
        like = f"%{keyword}%"
        stmt = stmt.where(
            or_(User.username.like(like), User.email.like(like), User.real_name.like(like))
        )
    if role:
        stmt = stmt.where(User.role == role)

    total = db.scalar(select(func.count()).select_from(stmt.subquery())) or 0
    rows = db.scalars(
        stmt.order_by(User.created_at.desc()).offset((page - 1) * size).limit(size)
    ).all()
    return list(rows), total


def count_all(db: Session) -> int:
    from sqlalchemy import func

    return db.scalar(select(func.count(User.id))) or 0
