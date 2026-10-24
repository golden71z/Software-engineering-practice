"""用户相关的出入参对象。

对应 Java 的 DTO（入参）与 VO（出参）。
刻意分成多个类而不是复用 User 模型：
- UserCreate 只包含"注册时允许传的字段"
- UserOut 只包含"允许返回给前端的字段"（绝不含 password_hash）
"""
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserCreate(BaseModel):
    """注册入参。"""

    username: str = Field(min_length=3, max_length=32, description="登录名，3-32 位")
    password: str = Field(min_length=6, max_length=64, description="密码，至少 6 位")
    email: EmailStr = Field(description="邮箱")
    real_name: str | None = Field(default=None, max_length=32, description="真实姓名")
    phone: str | None = Field(default=None, max_length=20, description="手机号")


class UserLogin(BaseModel):
    """登录入参。"""

    username: str = Field(description="登录名或邮箱")
    password: str = Field(description="密码")


class UserOut(BaseModel):
    """用户出参。from_attributes 让它可以由 ORM 对象直接转换。"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    email: str
    real_name: str | None = None
    phone: str | None = None
    role: str
    status: int
    created_at: datetime


class TokenOut(BaseModel):
    """登录成功后返回的令牌。"""

    access_token: str
    token_type: str = "bearer"
    expires_in: int = Field(description="有效期（秒）")
