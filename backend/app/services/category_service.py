"""分类业务逻辑层。

删除策略：分类被物品引用过就不允许物理删除，只能停用。
理由：物理删除会让历史物品的 category_id 变成悬空外键，
列表页取不到分类名就会显示空白，排查起来很烦。
"""
from sqlalchemy.orm import Session

from app.core.exceptions import BusinessError, NotFoundError
from app.models.category import Category
from app.repositories import category_repo
from app.schemas.category import CategoryCreate, CategoryUpdate


def list_categories(db: Session, only_active: bool = True) -> list[Category]:
    return category_repo.list_categories(db, only_active=only_active)


def create_category(db: Session, payload: CategoryCreate) -> Category:
    if category_repo.get_by_name(db, payload.name):
        raise BusinessError("该分类已存在")
    category = category_repo.create(db, payload.name, payload.sort_order)
    db.commit()
    db.refresh(category)
    return category


def update_category(db: Session, category_id: int, payload: CategoryUpdate) -> Category:
    category = category_repo.get_by_id(db, category_id)
    if category is None:
        raise NotFoundError("分类不存在")

    data = payload.model_dump(exclude_unset=True)
    new_name = data.get("name")
    if new_name and new_name != category.name:
        if category_repo.get_by_name(db, new_name):
            raise BusinessError("该分类名称已被占用")

    for field, value in data.items():
        if value is not None:
            setattr(category, field, value)

    db.commit()
    db.refresh(category)
    return category


def delete_category(db: Session, category_id: int) -> None:
    category = category_repo.get_by_id(db, category_id)
    if category is None:
        raise NotFoundError("分类不存在")

    used = category_repo.count_items(db, category_id)
    if used > 0:
        raise BusinessError(f"该分类下还有 {used} 条信息，请先停用而不是删除")

    db.delete(category)
    db.commit()
