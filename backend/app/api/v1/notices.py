"""公告接口。读公开，写仅管理员。"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import require_admin
from app.db.session import get_db
from app.models.user import User
from app.schemas.common import ApiResponse
from app.schemas.notice import NoticeCreate, NoticeOut
from app.services import notice_service

router = APIRouter(tags=["公告"])


@router.get("", response_model=ApiResponse[list[NoticeOut]], summary="公告列表")
def list_notices(
    limit: int | None = Query(None, ge=1, le=50, description="最多返回几条"),
    db: Session = Depends(get_db),
) -> ApiResponse[list[NoticeOut]]:
    notices = notice_service.list_notices(db, limit)
    return ApiResponse[list[NoticeOut]](
        data=[NoticeOut.model_validate(n) for n in notices]
    )


@router.post("", response_model=ApiResponse[NoticeOut], summary="发布公告（管理员）")
def create_notice(
    payload: NoticeCreate,
    db: Session = Depends(get_db),
    current: User = Depends(require_admin),
) -> ApiResponse[NoticeOut]:
    notice = notice_service.create_notice(db, current, payload)
    return ApiResponse[NoticeOut](
        message="发布成功", data=NoticeOut.model_validate(notice)
    )


@router.delete("/{notice_id}", response_model=ApiResponse[None], summary="删除公告（管理员）")
def delete_notice(
    notice_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
) -> ApiResponse[None]:
    notice_service.delete_notice(db, notice_id)
    return ApiResponse[None](message="删除成功")
