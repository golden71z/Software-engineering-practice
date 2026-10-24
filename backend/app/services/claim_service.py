"""认领业务逻辑层。

认领是本系统最需要"规则"的地方，核心三条：
1. 不能认领自己发布的信息（否则等于自己给自己发申请）
2. 同一人对同一物品只能有一条有效申请
3. 一条申请通过后，物品置为已归还，同一物品的其他待处理申请自动拒绝
"""
from datetime import datetime

from sqlalchemy.orm import Session

from app.core.exceptions import BusinessError, ForbiddenError, NotFoundError
from app.models.claim import Claim
from app.models.user import User
from app.repositories import claim_repo, item_repo
from app.schemas.claim import ClaimCreate


def apply(db: Session, applicant: User, payload: ClaimCreate) -> Claim:
    item = item_repo.get_by_id(db, payload.item_id)
    if item is None:
        raise NotFoundError("该信息不存在")
    if item.publisher_id == applicant.id:
        raise BusinessError("不能认领自己发布的信息")
    if item.status != "published":
        raise BusinessError("该信息当前不接受认领")

    if claim_repo.get_active(db, item.id, applicant.id):
        raise BusinessError("你已经提交过认领申请，请等待处理")

    claim = claim_repo.create(
        db,
        item_id=item.id,
        applicant_id=applicant.id,
        proof=payload.proof,
        contact=payload.contact or applicant.phone,
        status="pending",
    )
    db.commit()
    db.refresh(claim)
    return claim


def list_mine(db: Session, applicant: User) -> list[Claim]:
    return claim_repo.list_by_applicant(db, applicant.id)


def list_received(db: Session, owner: User, status: str | None) -> list[Claim]:
    return claim_repo.list_by_owner(db, owner.id, status=status or None)


def count_pending(db: Session, owner: User) -> int:
    return claim_repo.count_pending_by_owner(db, owner.id)


def _get_for_handler(db: Session, claim_id: int, handler: User) -> Claim:
    claim = claim_repo.get_by_id(db, claim_id)
    if claim is None:
        raise NotFoundError("认领申请不存在")
    if claim.item is None:
        raise NotFoundError("关联的信息已不存在")
    if claim.item.publisher_id != handler.id and handler.role != "admin":
        raise ForbiddenError("只有信息发布者或管理员能处理该申请")
    return claim


def approve(db: Session, handler: User, claim_id: int, comment: str | None) -> Claim:
    claim = _get_for_handler(db, claim_id, handler)
    if claim.status != "pending":
        raise BusinessError("该申请已被处理过了")

    claim.status = "approved"
    claim.handled_by = handler.id
    claim.handle_comment = comment or "认领已通过"
    claim.handled_at = datetime.now()

    # 物品置为已归还，并自动拒绝同一物品的其他申请
    item = claim.item
    item_repo.mark_returned(db, item, datetime.now())
    claim_repo.reject_others(
        db,
        item_id=item.id,
        keep_id=claim.id,
        handler_id=handler.id,
        comment="该物品已由其他人认领成功",
    )

    db.commit()
    db.refresh(claim)
    return claim


def reject(db: Session, handler: User, claim_id: int, comment: str | None) -> Claim:
    claim = _get_for_handler(db, claim_id, handler)
    if claim.status != "pending":
        raise BusinessError("该申请已被处理过了")

    claim.status = "rejected"
    claim.handled_by = handler.id
    claim.handle_comment = comment or "认领信息不匹配"
    claim.handled_at = datetime.now()
    db.commit()
    db.refresh(claim)
    return claim


def cancel(db: Session, applicant: User, claim_id: int) -> Claim:
    """申请人自己撤销，避免误提交后一直卡着。"""
    claim = claim_repo.get_by_id(db, claim_id)
    if claim is None:
        raise NotFoundError("认领申请不存在")
    if claim.applicant_id != applicant.id:
        raise ForbiddenError("只能撤销自己的申请")
    if claim.status != "pending":
        raise BusinessError("只有待处理的申请才能撤销")

    claim.status = "cancelled"
    claim.handled_at = datetime.now()
    claim.handle_comment = "申请人已撤销"
    db.commit()
    db.refresh(claim)
    return claim
