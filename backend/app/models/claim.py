"""认领申请表。

流程：申请人提交（pending）→ 物品发布者初审（approved / rejected）
     → approved 后物品自动置为 returned。

约束：同一用户对同一物品只允许存在一条有效申请，
由 (item_id, applicant_id) 唯一索引兜底，防止连点提交重复数据。
"""
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.item import Item
from app.models.user import User


class Claim(Base):
    __tablename__ = "claims"
    __table_args__ = (
        UniqueConstraint("item_id", "applicant_id", name="uq_claim_item_applicant"),
        {"comment": "认领申请表"},
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, comment="主键")
    item_id: Mapped[int] = mapped_column(
        ForeignKey("items.id"), index=True, nullable=False, comment="物品"
    )
    applicant_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"), index=True, nullable=False, comment="申请人"
    )
    proof: Mapped[str] = mapped_column(
        Text, nullable=False, comment="认领说明/凭证，例如物品特征、内含物"
    )
    contact: Mapped[str | None] = mapped_column(
        String(64), default=None, comment="申请人联系方式"
    )
    status: Mapped[str] = mapped_column(
        String(16),
        default="pending",
        index=True,
        nullable=False,
        comment="pending 待处理 / approved 通过 / rejected 拒绝 / cancelled 已撤销",
    )
    handled_by: Mapped[int | None] = mapped_column(
        ForeignKey("users.id"), default=None, comment="处理人（物品发布者）"
    )
    handle_comment: Mapped[str | None] = mapped_column(
        String(255), default=None, comment="处理意见"
    )
    handled_at: Mapped[datetime | None] = mapped_column(
        DateTime, default=None, comment="处理时间"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False, comment="申请时间"
    )

    item: Mapped[Item] = relationship(lazy="joined")
    # 本表有两个指向 users 的外键，必须显式指明用哪一个
    applicant: Mapped[User] = relationship(foreign_keys=[applicant_id], lazy="joined")

    def __repr__(self) -> str:
        return f"<Claim id={self.id} item_id={self.item_id} status={self.status!r}>"
