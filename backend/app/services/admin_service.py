"""管理端业务逻辑层：数据看板 + 用户管理。"""
from sqlalchemy.orm import Session

from app.core.exceptions import BusinessError, NotFoundError
from app.models.user import User
from app.repositories import category_repo, claim_repo, item_repo, user_repo


def dashboard(db: Session) -> dict:
    """汇总看板数据。

    指标口径（写进文档时要说明白）：
    - 归还率 = 已归还条数 / 全部发布条数（含已下架，因为下架不代表没归还）
    - 平均归还耗时 = AVG(returned_at - created_at)，只统计已归还记录
    """
    overview = item_repo.stats_overview(db)

    categories = category_repo.list_categories(db, only_active=False)
    name_map = {str(c.id): c.name for c in categories}
    distribution = [
        {"name": name_map.get(cid, "未分类"), "value": count, "category_id": int(cid)}
        for cid, count in item_repo.stats_by_category(db)
    ]

    overview["category_distribution"] = distribution
    overview["type_distribution"] = [
        {"name": "失物", "value": overview["lost"]},
        {"name": "招领", "value": overview["found"]},
    ]
    overview["user_count"] = user_repo.count_all(db)
    overview["pending_claims"] = claim_repo.count_all_pending(db)
    return overview


def list_users(
    db: Session, *, keyword: str | None, role: str | None, page: int, size: int
) -> tuple[list[User], int]:
    return user_repo.search(
        db,
        keyword=keyword,
        role=role,
        page=max(page, 1),
        size=min(max(size, 1), 100),
    )


def set_user_status(db: Session, operator: User, user_id: int, status: int) -> User:
    """启用 / 禁用账号。"""
    if status not in (0, 1):
        raise BusinessError("状态值只能是 0 或 1")

    target = user_repo.get_by_id(db, user_id)
    if target is None:
        raise NotFoundError("用户不存在")
    if target.id == operator.id:
        raise BusinessError("不能修改自己的账号状态")
    if target.role == "admin":
        raise BusinessError("不能禁用管理员账号")

    target.status = status
    db.commit()
    db.refresh(target)
    return target
