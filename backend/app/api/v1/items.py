"""物品接口。

路由顺序有讲究：`/mine` 必须写在 `/{item_id}` 前面。
FastAPI 按声明顺序匹配，如果 `/{item_id}` 在前，"mine" 会被当成 ID 解析而报 422。
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_optional_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.common import ApiResponse, PageOut
from app.schemas.item import ItemCreate, ItemDetailOut, ItemOut, ItemUpdate
from app.services import item_service

router = APIRouter(tags=["物品"])


@router.get("", response_model=ApiResponse[PageOut[ItemOut]], summary="物品列表（公开）")
def list_items(
    type_: str | None = Query(None, alias="type", description="lost / found，不传为全部"),
    category_id: int | None = Query(None, description="分类 ID"),
    keyword: str | None = Query(None, description="标题/描述/地点关键词"),
    page: int = Query(1, ge=1),
    size: int = Query(12, ge=1, le=100),
    db: Session = Depends(get_db),
) -> ApiResponse[PageOut[ItemOut]]:
    rows, total = item_service.list_items(
        db,
        type_=type_,
        category_id=category_id,
        keyword=keyword,
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


@router.get(
    "/mine", response_model=ApiResponse[PageOut[ItemOut]], summary="我发布的信息"
)
def list_my_items(
    status: str | None = Query(None, description="published / returned / offline"),
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
) -> ApiResponse[PageOut[ItemOut]]:
    rows, total = item_service.list_mine(db, current, status, page, size)
    return ApiResponse[PageOut[ItemOut]](
        data=PageOut[ItemOut](
            items=[ItemOut.from_model(i) for i in rows],
            total=total,
            page=page,
            size=size,
        )
    )


@router.get(
    "/{item_id}", response_model=ApiResponse[ItemDetailOut], summary="物品详情"
)
def get_item(
    item_id: int,
    db: Session = Depends(get_db),
    viewer: User | None = Depends(get_optional_user),
) -> ApiResponse[ItemDetailOut]:
    item = item_service.get_detail(db, item_id, viewer)
    detail = ItemDetailOut.from_model(item)

    # 游客拿不到联系方式：防止爬虫把全校手机号批量抓走
    if viewer is None:
        detail.contact = None
        detail.publisher_phone = None

    return ApiResponse[ItemDetailOut](data=detail)


@router.post("", response_model=ApiResponse[ItemOut], summary="发布失物/招领")
def create_item(
    payload: ItemCreate,
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
) -> ApiResponse[ItemOut]:
    item = item_service.create_item(db, current, payload)
    return ApiResponse[ItemOut](message="发布成功", data=ItemOut.from_model(item))


@router.put("/{item_id}", response_model=ApiResponse[ItemOut], summary="编辑（本人）")
def update_item(
    item_id: int,
    payload: ItemUpdate,
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
) -> ApiResponse[ItemOut]:
    item = item_service.update_item(db, current, item_id, payload)
    return ApiResponse[ItemOut](message="修改成功", data=ItemOut.from_model(item))


@router.post(
    "/{item_id}/offline", response_model=ApiResponse[ItemOut], summary="下架（本人或管理员）"
)
def offline_item(
    item_id: int,
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
) -> ApiResponse[ItemOut]:
    item = item_service.offline_item(db, current, item_id)
    return ApiResponse[ItemOut](message="已下架", data=ItemOut.from_model(item))


@router.post(
    "/{item_id}/restore", response_model=ApiResponse[ItemOut], summary="重新上架（本人）"
)
def restore_item(
    item_id: int,
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
) -> ApiResponse[ItemOut]:
    item = item_service.restore_item(db, current, item_id)
    return ApiResponse[ItemOut](message="已重新上架", data=ItemOut.from_model(item))


@router.post(
    "/{item_id}/returned", response_model=ApiResponse[ItemOut], summary="标记已归还（本人）"
)
def mark_returned(
    item_id: int,
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
) -> ApiResponse[ItemOut]:
    item = item_service.mark_returned(db, current, item_id)
    return ApiResponse[ItemOut](message="已标记归还", data=ItemOut.from_model(item))
