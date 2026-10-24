"""物品业务逻辑层。

这里集中了"谁能改什么"的规则：
- 只有发布者本人能编辑、标记归还
- 发布者本人或管理员能下架
- 已归还的信息不允许再编辑
规则写在这一层，路由层就不需要 if，repository 也不需要知道用户是谁。
"""
from datetime import datetime

from sqlalchemy.orm import Session

from app.core.exceptions import BusinessError, ForbiddenError, NotFoundError
from app.models.item import Item
from app.models.user import User
from app.repositories import category_repo, item_repo
from app.schemas.item import ItemCreate, ItemUpdate


def list_items(
    db: Session,
    *,
    type_: str | None = None,
    category_id: int | None = None,
    keyword: str | None = None,
    status: str | None = "published",
    page: int = 1,
    size: int = 12,
) -> tuple[list[Item], int]:
    # "all" 是给管理端用的：不加状态条件，已下架的也能看到
    if status in ("all", ""):
        status = None
    page = max(page, 1)
    size = min(max(size, 1), 100)
    return item_repo.search(
        db,
        type_=type_,
        category_id=category_id,
        status=status,
        keyword=keyword,
        page=page,
        size=size,
    )


def list_mine(db: Session, publisher: User, status: str | None, page: int, size: int):
    return item_repo.search(
        db,
        publisher_id=publisher.id,
        status=status or None,
        page=max(page, 1),
        size=min(max(size, 1), 100),
    )


def get_detail(db: Session, item_id: int, viewer: User | None) -> Item:
    item = item_repo.get_by_id(db, item_id)
    if item is None:
        raise NotFoundError("该信息不存在或已被删除")

    # 已下架的信息只有发布者本人和管理员能看到
    if item.status == "offline":
        is_owner = viewer is not None and viewer.id == item.publisher_id
        is_admin = viewer is not None and viewer.role == "admin"
        if not (is_owner or is_admin):
            raise NotFoundError("该信息已下架")

    item_repo.increase_view(db, item)
    db.commit()
    db.refresh(item)
    return item


def create_item(db: Session, publisher: User, payload: ItemCreate) -> Item:
    category = category_repo.get_by_id(db, payload.category_id)
    if category is None or category.is_active != 1:
        raise BusinessError("分类不存在或已停用")

    item = item_repo.create(
        db,
        type=payload.type,
        title=payload.title,
        description=payload.description,
        category_id=payload.category_id,
        publisher_id=publisher.id,
        status="published",
        event_time=payload.event_time,
        location=payload.location,
        contact=payload.contact,
        images=",".join(payload.images),
        view_count=0,
    )
    db.commit()
    db.refresh(item)
    return item


def _get_own_item(db: Session, item_id: int, user: User) -> Item:
    """取出一条属于当前用户的信息，不属于就报错。"""
    item = item_repo.get_by_id(db, item_id)
    if item is None:
        raise NotFoundError("该信息不存在")
    if item.publisher_id != user.id:
        raise ForbiddenError("只能操作自己发布的信息")
    return item


def update_item(db: Session, user: User, item_id: int, payload: ItemUpdate) -> Item:
    item = _get_own_item(db, item_id, user)
    if item.status == "returned":
        raise BusinessError("已归还的信息不能修改")

    data = payload.model_dump(exclude_unset=True)
    if "category_id" in data:
        category = category_repo.get_by_id(db, data["category_id"])
        if category is None or category.is_active != 1:
            raise BusinessError("分类不存在或已停用")
    if "images" in data:
        data["images"] = ",".join(data["images"] or [])

    for field, value in data.items():
        setattr(item, field, value)

    db.commit()
    db.refresh(item)
    return item


def offline_item(db: Session, user: User, item_id: int) -> Item:
    """下架。发布者本人或管理员都可以操作。"""
    item = item_repo.get_by_id(db, item_id)
    if item is None:
        raise NotFoundError("该信息不存在")
    if item.publisher_id != user.id and user.role != "admin":
        raise ForbiddenError("无权下架该信息")
    if item.status == "offline":
        raise BusinessError("该信息已经是下架状态")

    item.status = "offline"
    db.commit()
    db.refresh(item)
    return item


def mark_returned(db: Session, user: User, item_id: int) -> Item:
    """发布者手动标记"已归还"（也由认领审批通过时自动触发）。"""
    item = _get_own_item(db, item_id, user)
    if item.status == "returned":
        raise BusinessError("该信息已标记为归还")
    item_repo.mark_returned(db, item, datetime.now())
    db.commit()
    db.refresh(item)
    return item


def restore_item(db: Session, user: User, item_id: int) -> Item:
    """把下架的信息重新上架（仅本人）。"""
    item = _get_own_item(db, item_id, user)
    if item.status != "offline":
        raise BusinessError("只有已下架的信息才能重新上架")
    item.status = "published"
    db.commit()
    db.refresh(item)
    return item
