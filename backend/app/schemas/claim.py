"""认领申请相关的出入参。"""
from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class ClaimCreate(BaseModel):
    item_id: int
    proof: str = Field(min_length=5, max_length=1000, description="认领说明，越具体越好")
    contact: str | None = Field(default=None, max_length=64)


class ClaimHandle(BaseModel):
    comment: str | None = Field(default=None, max_length=255, description="处理意见")


class ClaimOut(BaseModel):
    id: int
    item_id: int
    item_title: str
    item_type: str
    applicant_id: int
    applicant_name: str
    proof: str
    contact: str | None
    status: str
    handle_comment: str | None
    handled_at: datetime | None
    created_at: datetime

    @classmethod
    def from_model(cls, claim: Any) -> "ClaimOut":
        return cls(
            id=claim.id,
            item_id=claim.item_id,
            item_title=claim.item.title if claim.item else "",
            item_type=claim.item.type if claim.item else "",
            applicant_id=claim.applicant_id,
            applicant_name=claim.applicant.username if claim.applicant else "",
            proof=claim.proof,
            contact=claim.contact,
            status=claim.status,
            handle_comment=claim.handle_comment,
            handled_at=claim.handled_at,
            created_at=claim.created_at,
        )
