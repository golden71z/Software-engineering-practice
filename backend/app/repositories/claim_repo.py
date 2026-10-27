"""认领申请数据访问层。"""
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.claim import Claim
from app.models.item import Item


def get_by_id(db: Session, claim_id: int) -> Claim | None:
    return db.get(Claim, claim_id)


def get_active(db: Session, item_id: int, applicant_id: int) -> Claim | None:
    """查同一个人对同一物品是否已有未撤销的申请。"""
    return db.scalar(
        select(Claim).where(
            Claim.item_id == item_id,
            Claim.applicant_id == applicant_id,
            Claim.status.in_(["pending", "approved"]),
        )
    )


def create(db: Session, **fields) -> Claim:
    claim = Claim(**fields)
    db.add(claim)
    db.flush()
    return claim


def list_by_applicant(db: Session, applicant_id: int) -> list[Claim]:
    stmt = (
        select(Claim)
        .where(Claim.applicant_id == applicant_id)
        .order_by(Claim.created_at.desc())
    )
    return list(db.scalars(stmt).all())


def list_by_owner(
    db: Session,
    owner_id: int,
    status: str | None = None,
    item_id: int | None = None,
) -> list[Claim]:
    """物品发布者查看自己收到的申请，可按状态、按物品过滤。"""
    stmt = select(Claim).join(Item, Claim.item_id == Item.id).where(
        Item.publisher_id == owner_id
    )
    if status:
        stmt = stmt.where(Claim.status == status)
    if item_id:
        stmt = stmt.where(Claim.item_id == item_id)
    stmt = stmt.order_by(Claim.created_at.desc())
    return list(db.scalars(stmt).all())


def count_pending_by_owner(db: Session, owner_id: int) -> int:
    """待处理申请数，用于导航角标。"""
    return (
        db.scalar(
            select(func.count(Claim.id))
            .join(Item, Claim.item_id == Item.id)
            .where(Item.publisher_id == owner_id, Claim.status == "pending")
        )
        or 0
    )


def has_approved(db: Session, item_id: int) -> bool:
    return (
        db.scalar(
            select(Claim.id).where(Claim.item_id == item_id, Claim.status == "approved")
        )
        is not None
    )


def count_all_pending(db: Session) -> int:
    """全站待处理申请数，管理端看板用。"""
    return db.scalar(select(func.count(Claim.id)).where(Claim.status == "pending")) or 0


def reject_others(db: Session, item_id: int, keep_id: int, handler_id: int, comment: str) -> None:
    """一条申请通过后，其余待处理申请自动置为已拒绝（物品只有一个）。

    这是业务上的"排他"处理：不这么做，同一件物品会被多人"认领成功"。
    """
    from datetime import datetime

    stmt = select(Claim).where(
        Claim.item_id == item_id,
        Claim.status == "pending",
        Claim.id != keep_id,
    )
    for other in db.scalars(stmt).all():
        other.status = "rejected"
        other.handled_by = handler_id
        other.handle_comment = comment
        other.handled_at = datetime.now()
