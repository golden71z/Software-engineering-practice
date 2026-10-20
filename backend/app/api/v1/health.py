"""健康检查接口。

用途有两个：
1. 前端联调时确认"后端到底通不通"
2. 顺带探测数据库是否可用（不会因为数据库挂了就让接口报错）
"""
from fastapi import APIRouter
from sqlalchemy import text

from app.core.config import settings
from app.db.session import SessionLocal
from app.schemas.common import ApiResponse

router = APIRouter(tags=["系统"])


@router.get("/health", response_model=ApiResponse[dict], summary="健康检查")
def health() -> ApiResponse[dict]:
    db_ok = True
    db_error: str | None = None

    try:
        with SessionLocal() as db:
            db.execute(text("SELECT 1"))
    except Exception as exc:  # 数据库不可用时不让整个接口失败
        db_ok = False
        db_error = str(exc).splitlines()[0][:200]

    return ApiResponse[dict](
        data={
            "service": settings.APP_NAME,
            "version": settings.APP_VERSION,
            "status": "UP" if db_ok else "DEGRADED",
            "database": "UP" if db_ok else "DOWN",
            "database_error": db_error,
        }
    )
