"""物品数据访问层。

搜索用的是一个"按需拼条件"的写法：传了什么就加什么 WHERE，
不传就不限制。这样列表页和"我的发布"可以复用同一个函数。
"""
from datetime import datetime

from sqlalchemy import Select, func, or_, select, text
from sqlalchemy.orm import Session

from app.models.item import Item


def _build_stmt(
    *,
    type_: str | None = None,
    category_id: int | None = None,
    status: str | None = None,
    keyword: str | None = None,
    publisher_id: int | None = None,
) -> Select:
    stmt = select(Item)
    if type_:
        stmt = stmt.where(Item.type == type_)
    if category_id:
        stmt = stmt.where(Item.category_id == category_id)
    if status:
        stmt = stmt.where(Item.status == status)
    if publisher_id:
        stmt = stmt.where(Item.publisher_id == publisher_id)
    if keyword:
        like = f"%{keyword}%"
        stmt = stmt.where(
            or_(
                Item.title.like(like),
                Item.description.like(like),
                Item.location.like(like),
            )
        )
    return stmt


def search(
    db: Session,
    *,
    type_: str | None = None,
    category_id: int | None = None,
    status: str | None = "published",
    keyword: str | None = None,
    publisher_id: int | None = None,
    page: int = 1,
    size: int = 12,
) -> tuple[list[Item], int]:
    """返回 (当前页数据, 总条数)。"""
    stmt = _build_stmt(
        type_=type_,
        category_id=category_id,
        status=status,
        keyword=keyword,
        publisher_id=publisher_id,
    )
    total = db.scalar(select(func.count()).select_from(stmt.subquery())) or 0
    rows = db.scalars(
        stmt.order_by(Item.created_at.desc()).offset((page - 1) * size).limit(size)
    ).all()
    return list(rows), total


def get_by_id(db: Session, item_id: int) -> Item | None:
    return db.get(Item, item_id)


def create(db: Session, **fields) -> Item:
    item = Item(**fields)
    db.add(item)
    db.flush()
    return item


def increase_view(db: Session, item: Item) -> None:
    """浏览计数用 SQL 自增，避免并发送读改写丢计数。"""
    item.view_count = (item.view_count or 0) + 1


def mark_returned(db: Session, item: Item, when: datetime) -> None:
    item.status = "returned"
    item.returned_at = when


def stats_overview(db: Session) -> dict:
    """管理端看板的核心指标，一条 SQL 全部算完。"""
    total = db.scalar(select(func.count(Item.id))) or 0
    published = db.scalar(
        select(func.count(Item.id)).where(Item.status == "published")
    ) or 0
    returned = db.scalar(select(func.count(Item.id)).where(Item.status == "returned")) or 0
    offline = db.scalar(select(func.count(Item.id)).where(Item.status == "offline")) or 0
    lost = db.scalar(select(func.count(Item.id)).where(Item.type == "lost")) or 0
    found = db.scalar(select(func.count(Item.id)).where(Item.type == "found")) or 0

    # 平均归还耗时（小时）：只算已归还且有创建时间的记录。
    # timestampdiff 的第一个参数必须是字面量，用 text("second") 而不是 func.second，
    # 否则 SQLAlchemy 会把它当成一个函数对象拼进 SQL，MySQL 直接语法报错。
    avg_seconds = db.scalar(
        select(
            func.avg(
                func.timestampdiff(text("second"), Item.created_at, Item.returned_at)
            )
        ).where(Item.returned_at.is_not(None))
    )

    return {
        "total": total,
        "published": published,
        "returned": returned,
        "offline": offline,
        "lost": lost,
        "found": found,
        "return_rate": round(returned / total * 100, 1) if total else 0.0,
        "avg_return_hours": round(float(avg_seconds) / 3600, 1) if avg_seconds else 0.0,
    }


def stats_by_category(db: Session) -> list[tuple[str, int]]:
    """分类分布，用于看板饼图。"""
    rows = db.execute(
        select(Item.category_id, func.count(Item.id)).group_by(Item.category_id)
    ).all()
    return [(str(cid), cnt) for cid, cnt in rows]
