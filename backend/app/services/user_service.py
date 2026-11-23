"""用户业务逻辑层。

只处理"规则"：用户名是否重复、密码对不对、账号是否被禁用、令牌怎么发。
不关心数据是怎么从数据库取出来的（那是 repository 的事），
也不关心怎么序列化给前端（那是 schema 的事）。
"""
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.core.config import settings
from app.core.exceptions import BusinessError, UnauthorizedError
from app.core.security import create_access_token, hash_password, verify_password
from app.models.user import User
from app.repositories import user_repo
from app.schemas.user import PasswordChange, ProfileUpdate, UserCreate


def register(db: Session, payload: UserCreate) -> User:
    """注册新用户。"""
    if user_repo.exists_username(db, payload.username):
        raise BusinessError("该用户名已被占用")
    if user_repo.exists_email(db, payload.email):
        raise BusinessError("该邮箱已被注册")

    user = user_repo.create(
        db,
        username=payload.username,
        email=payload.email,
        password_hash=hash_password(payload.password),
        real_name=payload.real_name,
        phone=payload.phone,
        role="user",
        status=1,
    )
    db.commit()
    db.refresh(user)
    return user


def login(db: Session, username: str, password: str) -> tuple[User, str]:
    """登录校验，返回 (用户, 令牌)。

    用户名不存在与密码错误返回同一句提示，避免泄露"哪些账号存在"。
    """
    user = user_repo.get_by_username(db, username)
    if user is None or not verify_password(password, user.password_hash):
        raise BusinessError("用户名或密码错误")
    if user.status != 1:
        raise UnauthorizedError("账号已被禁用，请联系管理员")

    token = create_access_token(subject=str(user.id), extra={"role": user.role})
    return user, token


def token_expires_in() -> int:
    """令牌有效期（秒），给前端展示用。"""
    return settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60


def change_password(db: Session, current: User, payload: PasswordChange) -> None:
    """只允许当前用户校验原密码后修改自己的密码。"""
    if not verify_password(payload.current_password, current.password_hash):
        raise BusinessError("当前密码不正确")
    if verify_password(payload.new_password, current.password_hash):
        raise BusinessError("新密码不能与当前密码相同")
    current.password_hash = hash_password(payload.new_password)
    db.commit()


def update_profile(db: Session, current: User, payload: ProfileUpdate) -> User:
    existing = user_repo.get_by_email(db, payload.email)
    if existing is not None and existing.id != current.id:
        raise BusinessError("该邮箱已被其他账号使用")
    current.email = str(payload.email)
    current.real_name = payload.real_name
    current.phone = payload.phone
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise BusinessError("该邮箱已被其他账号使用") from exc
    db.refresh(current)
    return current
