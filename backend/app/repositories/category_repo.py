"""分类数据访问层。"""
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.category import Category
from app.models.item import Item


def list_categories(db: Session, only_active: bool = True) -> list[Category]:
    stmt = select(Category)
    if only_active:
        stmt = stmt.where(Category.is_active == 1)
    stmt = stmt.order_by(Category.sort_order.asc(), Category.id.asc())
    return list(db.scalars(stmt).all())


def get_by_id(db: Session, category_id: int) -> Category | None:
    return db.get(Category, category_id)


def get_by_name(db: Session, name: str) -> Category | None:
    return db.scalar(select(Category).where(Category.name == name))


def create(db: Session, name: str, sort_order: int = 0) -> Category:
    category = Category(name=name, sort_order=sort_order, is_active=1)
    db.add(category)
    db.flush()
    return category


def count_items(db: Session, category_id: int) -> int:
    """统计该分类下有多少物品，用于判断能否物理删除。"""
    return db.scalar(select(func.count(Item.id)).where(Item.category_id == category_id)) or 0
