"""失物 / 招领信息表。

设计决策：失物（lost）与招领（found）共用一张表，用 type 字段区分。
理由：两者字段完全一致（标题、描述、分类、地点、时间、图片、联系人），
只有"语义"不同。分两张表会导致检索、分页、统计都要写两遍 union。

status 取值：
- published 展示中（默认）
- returned  已归还
- offline   已下架（本人或管理员操作）

注意：没有"待审核"状态。本系统采用"发布即展示 + 事后下架"策略，
把审核成本从"事前拦每一篇"降为"事后处理举报"，代价是有短暂的风险窗口。
"""
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.category import Category
from app.models.user import User


class Item(Base):
    __tablename__ = "items"
    __table_args__ = {"comment": "失物招领信息表"}

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, comment="主键")
    type: Mapped[str] = mapped_column(
        String(8), index=True, nullable=False, comment="lost 失物 / found 招领"
    )
    title: Mapped[str] = mapped_column(String(100), nullable=False, comment="标题")
    description: Mapped[str] = mapped_column(
        Text, nullable=False, comment="详细描述（含特征，便于失主核对）"
    )
    category_id: Mapped[int] = mapped_column(
        ForeignKey("categories.id"), index=True, nullable=False, comment="分类"
    )
    publisher_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"), index=True, nullable=False, comment="发布者"
    )
    status: Mapped[str] = mapped_column(
        String(16),
        default="published",
        index=True,
        nullable=False,
        comment="published 展示中 / returned 已归还 / offline 已下架",
    )
    event_time: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, comment="丢失或拾获的时间"
    )
    location: Mapped[str] = mapped_column(
        String(100), nullable=False, comment="丢失或拾获的地点"
    )
    contact: Mapped[str | None] = mapped_column(
        String(64), default=None, comment="联系方式（仅登录用户可见）"
    )
    images: Mapped[str] = mapped_column(
        Text, default="", nullable=False, comment="图片相对路径，逗号分隔"
    )
    view_count: Mapped[int] = mapped_column(default=0, nullable=False, comment="浏览次数")
    returned_at: Mapped[datetime | None] = mapped_column(
        DateTime, default=None, comment="标记归还的时间，用于统计平均归还耗时"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False, comment="创建时间"
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
        comment="更新时间",
    )

    # 关系仅用于读取时预加载，避免列表页 N+1 查询
    category: Mapped[Category] = relationship(lazy="joined")
    publisher: Mapped[User] = relationship(lazy="joined")

    @property
    def image_list(self) -> list[str]:
        """把逗号分隔的字符串拆成列表，schema 层直接取用。"""
        return [part for part in self.images.split(",") if part]

    def __repr__(self) -> str:
        return f"<Item id={self.id} type={self.type!r} title={self.title!r}>"
