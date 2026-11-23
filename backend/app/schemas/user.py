"""用户相关的出入参对象。

对应 Java 的 DTO（入参）与 VO（出参）。
刻意分成多个类而不是复用 User 模型：
- UserCreate 只包含"注册时允许传的字段"
- UserOut 只包含"允许返回给前端的字段"（绝不含 password_hash）
"""
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


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


class ProfileUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    email: EmailStr = Field(max_length=128)
    real_name: str | None = Field(default=None, max_length=32)
    phone: str | None = Field(default=None, min_length=11, max_length=11, pattern=r"^1[3-9][0-9]{9}$")

    @field_validator("real_name", "phone", mode="before")
    @classmethod
    def empty_to_none(cls, value):
        return value.strip() or None if isinstance(value, str) else value


class PasswordChange(BaseModel):
    current_password: str = Field(min_length=1, max_length=64)
    new_password: str = Field(min_length=6, max_length=64)

    @field_validator("new_password")
    @classmethod
    def validate_password_bytes(cls, value: str) -> str:
        if len(value.encode("utf-8")) > 72:
            raise ValueError("新密码 UTF-8 长度不能超过 72 字节")
        return value


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
