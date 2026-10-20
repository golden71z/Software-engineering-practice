"""用户表 ORM 模型。

对应 Java 里的 entity。注意这里是"表结构"，不是接口出入参——
出入参在 app/schemas/user.py，两者刻意分开，避免表结构变动污染接口契约。
"""
from datetime import datetime

from sqlalchemy import DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class User(Base):
    __tablename__ = "users"
    __table_args__ = {"comment": "用户表"}

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, comment="主键")
    username: Mapped[str] = mapped_column(
        String(32), unique=True, index=True, nullable=False, comment="登录名"
    )
    email: Mapped[str] = mapped_column(
        String(128), unique=True, index=True, nullable=False, comment="邮箱"
    )
    password_hash: Mapped[str] = mapped_column(
        String(128), nullable=False, comment="bcrypt 密码哈希"
    )
    real_name: Mapped[str | None] = mapped_column(String(32), default=None, comment="真实姓名")
    phone: Mapped[str | None] = mapped_column(String(20), default=None, comment="手机号")
    role: Mapped[str] = mapped_column(
        String(16), default="user", nullable=False, comment="角色：user / admin"
    )
    status: Mapped[int] = mapped_column(default=1, nullable=False, comment="1 正常 0 禁用")
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False, comment="创建时间"
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now(), nullable=False, comment="更新时间"
    )

    def __repr__(self) -> str:
        return f"<User id={self.id} username={self.username!r} role={self.role!r}>"
