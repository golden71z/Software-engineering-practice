"""统一响应体。

所有接口都返回 {code, message, data} 三段结构：
- code = 20000 表示成功，其他值表示各类业务错误
- message 是给人看的提示
- data 是真正的业务数据

这样前端只需在 axios 拦截器里判断一次 code，不用为每个接口写不同的错误处理。
"""
from typing import Generic, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")

SUCCESS_CODE = 20000


class ApiResponse(BaseModel, Generic[T]):
    code: int = Field(default=SUCCESS_CODE, description="20000 表示成功")
    message: str = Field(default="success", description="提示信息")
    data: T | None = Field(default=None, description="业务数据")


class PageOut(BaseModel, Generic[T]):
    """统一分页结构。所有列表接口都返回这四个字段，前端只需写一套分页组件。

    注意字段名用 items 而不是 list：`list: list[T]` 会让字段名遮蔽内建类型，
    Pydantic 解析注解时会拿到 FieldInfo 而报 TypeError。
    """

    items: list[T] = Field(default_factory=list, description="当前页数据")
    total: int = Field(default=0, description="总条数")
    page: int = Field(default=1, description="当前页码，从 1 开始")
    size: int = Field(default=12, description="每页条数")
