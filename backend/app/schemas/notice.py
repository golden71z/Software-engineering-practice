"""公告相关的出入参。"""
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class NoticeCreate(BaseModel):
    title: str = Field(min_length=2, max_length=100)
    content: str = Field(min_length=2, max_length=2000)
    is_top: int = Field(default=0, description="1 置顶")


class NoticeOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    content: str
    is_top: int
    created_at: datetime
