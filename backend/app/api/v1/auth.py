"""认证相关接口：注册 / 登录 / 获取当前用户。

路由层（Controller）只做三件事：接收入参、调用 service、包装成统一响应体。
不写业务判断，也不写 SQL。
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.common import ApiResponse
from app.schemas.user import TokenOut, UserCreate, UserLogin, UserOut
from app.services import user_service

router = APIRouter(tags=["认证"])


@router.post("/register", response_model=ApiResponse[UserOut], summary="用户注册")
def register(payload: UserCreate, db: Session = Depends(get_db)) -> ApiResponse[UserOut]:
    user = user_service.register(db, payload)
    return ApiResponse[UserOut](message="注册成功", data=UserOut.model_validate(user))


@router.post("/login", response_model=ApiResponse[TokenOut], summary="用户登录")
def login(payload: UserLogin, db: Session = Depends(get_db)) -> ApiResponse[TokenOut]:
    user, token = user_service.login(db, payload.username, payload.password)
    return ApiResponse[TokenOut](
        message="登录成功",
        data=TokenOut(
            access_token=token,
            expires_in=user_service.token_expires_in(),
        ),
    )


@router.get("/me", response_model=ApiResponse[UserOut], summary="获取当前登录用户")
def me(current: User = Depends(get_current_user)) -> ApiResponse[UserOut]:
    return ApiResponse[UserOut](data=UserOut.model_validate(current))
