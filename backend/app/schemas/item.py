"""物品相关的出入参。

ItemOut 与 ItemDetailOut 的差别就是"详情比列表多返回联系方式"：
列表页不需要知道谁的电话，只有真正点进详情、且已登录的人才看得到。
这样联系方式不会被爬虫批量抓走。
"""
from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field


class ItemCreate(BaseModel):
    type: Literal["lost", "found"] = Field(description="lost 失物 / found 招领")
    title: str = Field(min_length=2, max_length=100)
    description: str = Field(min_length=5, max_length=2000, description="详细描述")
    category_id: int
    event_time: datetime = Field(description="丢失或拾获时间")
    location: str = Field(min_length=2, max_length=100)
    contact: str | None = Field(default=None, max_length=64)
    images: list[str] = Field(default_factory=list, description="图片相对路径列表")


class ItemUpdate(BaseModel):
    """编辑时所有字段可选，只更新传了的。"""

    title: str | None = Field(default=None, min_length=2, max_length=100)
    description: str | None = Field(default=None, min_length=5, max_length=2000)
    category_id: int | None = None
    event_time: datetime | None = None
    location: str | None = Field(default=None, min_length=2, max_length=100)
    contact: str | None = Field(default=None, max_length=64)
    images: list[str] | None = None


class ItemOut(BaseModel):
    id: int
    type: str
    title: str
    description: str
    category_id: int
    category_name: str
    publisher_id: int
    publisher_name: str
    status: str
    event_time: datetime
    location: str
    images: list[str]
    view_count: int
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_model(cls, item: Any) -> "ItemOut":
        """从 ORM 对象组装。放在这里是为了让路由层保持"不写拼装逻辑"。"""
        return cls(
            id=item.id,
            type=item.type,
            title=item.title,
            description=item.description,
            category_id=item.category_id,
            category_name=item.category.name if item.category else "",
            publisher_id=item.publisher_id,
            publisher_name=item.publisher.username if item.publisher else "",
            status=item.status,
            event_time=item.event_time,
            location=item.location,
            images=item.image_list,
            view_count=item.view_count,
            created_at=item.created_at,
            updated_at=item.updated_at,
        )


class ItemDetailOut(ItemOut):
    """详情比列表多两样：联系方式、发布者手机号。"""

    contact: str | None = None
    publisher_phone: str | None = None

    @classmethod
    def from_model(cls, item: Any) -> "ItemDetailOut":
        base = ItemOut.from_model(item)
        return cls(
            **base.model_dump(),
            contact=item.contact,
            publisher_phone=item.publisher.phone if item.publisher else None,
        )
