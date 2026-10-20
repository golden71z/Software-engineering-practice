"""物品分类表。

分类是低频变更、高频读取的数据，前端可以一次性拉取后缓存。
管理员可以增删改，但被物品引用过的分类不允许物理删除（用 is_active 停用）。
"""
from datetime import datetime

from sqlalchemy import DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Category(Base):
    __tablename__ = "categories"
    __table_args__ = {"comment": "物品分类表"}

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, comment="主键")
    name: Mapped[str] = mapped_column(
        String(32), unique=True, nullable=False, comment="分类名称"
    )
    sort_order: Mapped[int] = mapped_column(
        default=0, nullable=False, comment="排序值，越小越靠前"
    )
    is_active: Mapped[int] = mapped_column(
        default=1, nullable=False, comment="1 启用 0 停用"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False, comment="创建时间"
    )

    def __repr__(self) -> str:
        return f"<Category id={self.id} name={self.name!r}>"
