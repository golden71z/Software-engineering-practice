"""分类相关的出入参。"""
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class CategoryCreate(BaseModel):
    name: str = Field(min_length=1, max_length=32, description="分类名称")
    sort_order: int = Field(default=0, description="排序值，越小越靠前")


class CategoryUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=32)
    sort_order: int | None = None
    is_active: int | None = Field(default=None, description="1 启用 0 停用")


class CategoryOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    sort_order: int
    is_active: int
    created_at: datetime | None = None
