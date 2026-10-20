"""分类接口。

读接口公开（前端进首页就要拿分类做筛选），写接口仅管理员。
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import require_admin
from app.db.session import get_db
from app.models.user import User
from app.schemas.category import CategoryCreate, CategoryOut, CategoryUpdate
from app.schemas.common import ApiResponse
from app.services import category_service

router = APIRouter(tags=["分类"])


@router.get(
    "",
    response_model=ApiResponse[list[CategoryOut]],
    summary="分类列表",
)
def list_categories(
    only_active: bool = Query(True, description="是否只返回启用的分类"),
    db: Session = Depends(get_db),
) -> ApiResponse[list[CategoryOut]]:
    categories = category_service.list_categories(db, only_active=only_active)
    return ApiResponse[list[CategoryOut]](
        data=[CategoryOut.model_validate(c) for c in categories]
    )


@router.post(
    "",
    response_model=ApiResponse[CategoryOut],
    summary="新增分类（管理员）",
)
def create_category(
    payload: CategoryCreate,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
) -> ApiResponse[CategoryOut]:
    category = category_service.create_category(db, payload)
    return ApiResponse[CategoryOut](
        message="新增成功", data=CategoryOut.model_validate(category)
    )


@router.put(
    "/{category_id}",
    response_model=ApiResponse[CategoryOut],
    summary="修改分类（管理员）",
)
def update_category(
    category_id: int,
    payload: CategoryUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
) -> ApiResponse[CategoryOut]:
    category = category_service.update_category(db, category_id, payload)
    return ApiResponse[CategoryOut](
        message="修改成功", data=CategoryOut.model_validate(category)
    )


@router.delete("/{category_id}", response_model=ApiResponse[None], summary="删除分类（管理员）")
def delete_category(
    category_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
) -> ApiResponse[None]:
    category_service.delete_category(db, category_id)
    return ApiResponse[None](message="删除成功")
