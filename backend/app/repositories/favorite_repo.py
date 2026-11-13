from sqlalchemy import delete, func, select
from sqlalchemy.orm import Session

from app.models.favorite import Favorite
from app.models.item import Item


def contains(db: Session, user_id: int, item_id: int) -> bool:
    return db.scalar(select(Favorite.id).where(Favorite.user_id == user_id, Favorite.item_id == item_id)) is not None


def add(db: Session, user_id: int, item_id: int) -> None:
    if not contains(db, user_id, item_id):
        db.add(Favorite(user_id=user_id, item_id=item_id))
        db.commit()


def remove(db: Session, user_id: int, item_id: int) -> None:
    db.execute(delete(Favorite).where(Favorite.user_id == user_id, Favorite.item_id == item_id))
    db.commit()


def remove_pending_check(db: Session, user_id: int, item_id: int) -> None:
    """Remove an item from the user's pending verification list in the current transaction."""
    db.execute(delete(Favorite).where(Favorite.user_id == user_id, Favorite.item_id == item_id))


def list_for_user(db: Session, user_id: int, page: int, size: int):
    base = select(Item).join(Favorite, Favorite.item_id == Item.id).where(
        Favorite.user_id == user_id, Item.status != "offline"
    )
    total = db.scalar(select(func.count()).select_from(base.subquery())) or 0
    items = db.scalars(base.order_by(Favorite.created_at.desc()).offset((page - 1) * size).limit(size)).all()
    return list(items), total
