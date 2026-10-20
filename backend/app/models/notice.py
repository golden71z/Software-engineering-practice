"""系统公告表。

只由管理员发布，所有访客可见。is_top 用于置顶重要通知。
"""
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Notice(Base):
    __tablename__ = "notices"
    __table_args__ = {"comment": "系统公告表"}

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, comment="主键")
    title: Mapped[str] = mapped_column(String(100), nullable=False, comment="标题")
    content: Mapped[str] = mapped_column(Text, nullable=False, comment="正文")
    publisher_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"), nullable=False, comment="发布人（管理员）"
    )
    is_top: Mapped[int] = mapped_column(default=0, nullable=False, comment="1 置顶")
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False, comment="发布时间"
    )

    def __repr__(self) -> str:
        return f"<Notice id={self.id} title={self.title!r}>"
