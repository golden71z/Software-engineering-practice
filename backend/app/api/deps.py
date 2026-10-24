"""公共依赖（Dependency）。

FastAPI 用 Depends() 做依赖注入，等价于 Spring 的 @Autowired + 拦截器，
但更直接：谁需要就在参数里声明一行，框架负责把值传进来。
"""
from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.exceptions import ForbiddenError, UnauthorizedError
from app.core.security import decode_token
from app.db.session import get_db
from app.models.user import User
from app.repositories import user_repo

# auto_error=False：令牌缺失时不由框架直接抛 403，交给我们返回统一响应体
bearer_scheme = HTTPBearer(auto_error=False, description="请求头格式：Bearer <token>")


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    """从请求头解析令牌，取出当前登录用户。对应 Java 的 JWT 拦截器。"""
    if credentials is None or not credentials.credentials:
        raise UnauthorizedError("缺少访问令牌")

    try:
        payload = decode_token(credentials.credentials)
    except Exception as exc:  # 过期、签名错、格式错都归到这里
        raise UnauthorizedError("令牌无效或已过期") from exc

    subject = payload.get("sub")
    try:
        user_id = int(subject)
    except (TypeError, ValueError) as exc:
        raise UnauthorizedError("令牌内容异常") from exc

    user = user_repo.get_by_id(db, user_id)
    if user is None:
        raise UnauthorizedError("用户不存在")
    if user.status != 1:
        raise UnauthorizedError("账号已被禁用")
    return user


def require_admin(current: User = Depends(get_current_user)) -> User:
    """要求管理员权限。在需要管理端接口时把它挂上去即可。"""
    if current.role != "admin":
        raise ForbiddenError("需要管理员权限")
    return current


def get_optional_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> User | None:
    """可选登录：带了有效令牌就返回用户，没带或无效就返回 None。

    用于"游客也能看，但登录后能看到更多"的接口，比如物品详情
    （游客看不到联系方式）。注意：令牌无效时静默返回 None 而不是报错，
    这样令牌过期的人浏览公开页面不会被强制踢出。
    """
    if credentials is None or not credentials.credentials:
        return None
    try:
        payload = decode_token(credentials.credentials)
        user_id = int(payload.get("sub"))
    except Exception:
        return None

    user = user_repo.get_by_id(db, user_id)
    if user is None or user.status != 1:
        return None
    return user
