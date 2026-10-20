"""管理端接口。

整组接口统一挂 require_admin 依赖，任何一个漏挂都会成为越权漏洞，
所以这里用 router 级别的 dependencies 一次性把住，而不是每个函数写一遍。
"""
from fastapi import APIRouter, Body, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import require_admin
from app.db.session import get_db
from app.models.user import User
from app.schemas.common import ApiResponse, PageOut
from app.schemas.item import ItemOut
from app.schemas.user import UserOut
from app.services import admin_service, item_service

router = APIRouter(
    tags=["管理端"],
    dependencies=[Depends(require_admin)],
    responses={403: {"description": "需要管理员权限"}},
)


@router.get("/dashboard", response_model=ApiResponse[dict], summary="数据看板")
def dashboard(db: Session = Depends(get_db)) -> ApiResponse[dict]:
    return ApiResponse[dict](data=admin_service.dashboard(db))


@router.get("/users", response_model=ApiResponse[PageOut[UserOut]], summary="用户列表")
def list_users(
    keyword: str | None = Query(None, description="用户名/邮箱/姓名关键词"),
    role: str | None = Query(None, description="user / admin"),
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
) -> ApiResponse[PageOut[UserOut]]:
    users, total = admin_service.list_users(
        db, keyword=keyword, role=role, page=page, size=size
    )
    return ApiResponse[PageOut[UserOut]](
        data=PageOut[UserOut](
            items=[UserOut.model_validate(u) for u in users],
            total=total,
            page=page,
            size=size,
        )
    )


@router.post(
    "/users/{user_id}/status", response_model=ApiResponse[UserOut], summary="启用/禁用用户"
)
def set_user_status(
    user_id: int,
    status: int = Body(..., embed=True, description="1 启用 0 禁用"),
    db: Session = Depends(get_db),
    current: User = Depends(require_admin),
) -> ApiResponse[UserOut]:
    user = admin_service.set_user_status(db, current, user_id, status)
    return ApiResponse[UserOut](
        message="已启用" if status == 1 else "已禁用",
        data=UserOut.model_validate(user),
    )


@router.get("/items", response_model=ApiResponse[PageOut[ItemOut]], summary="全部信息（含已下架）")
def list_all_items(
    type_: str | None = Query(None, alias="type"),
    category_id: int | None = Query(None),
    keyword: str | None = Query(None),
    status: str = Query("all", description="all / published / returned / offline"),
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
) -> ApiResponse[PageOut[ItemOut]]:
    rows, total = item_service.list_items(
        db,
        type_=type_,
        category_id=category_id,
        keyword=keyword,
        status=status,
        page=page,
        size=size,
    )
    return ApiResponse[PageOut[ItemOut]](
        data=PageOut[ItemOut](
            items=[ItemOut.from_model(i) for i in rows],
            total=total,
            page=page,
            size=size,
        )
    )
