"""业务异常与全局异常处理。

对应 Spring Boot 的 @RestControllerAdvice + @ExceptionHandler。
设计决策：业务错误一律返回 HTTP 200，错误码放在响应体的 code 字段里，
只有真正未预期的异常才返回 500。这样前端只需处理一套响应结构。
"""
import logging

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

logger = logging.getLogger(__name__)


class BusinessError(Exception):
    """业务规则不满足时抛出。会被全局处理器转成统一响应体。"""

    def __init__(self, message: str, code: int = 40000) -> None:
        self.message = message
        self.code = code
        super().__init__(message)


class UnauthorizedError(BusinessError):
    """未登录 / 令牌失效。"""

    def __init__(self, message: str = "登录已失效，请重新登录") -> None:
        super().__init__(message, code=40100)


class ForbiddenError(BusinessError):
    """已登录但无权限。"""

    def __init__(self, message: str = "没有操作权限") -> None:
        super().__init__(message, code=40300)


class NotFoundError(BusinessError):
    def __init__(self, message: str = "资源不存在") -> None:
        super().__init__(message, code=40400)


def _body(code: int, message: str, data=None) -> dict:
    return {"code": code, "message": message, "data": data}


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(BusinessError)
    async def handle_business(_: Request, exc: BusinessError) -> JSONResponse:
        return JSONResponse(status_code=200, content=_body(exc.code, exc.message))

    @app.exception_handler(RequestValidationError)
    async def handle_validation(_: Request, exc: RequestValidationError) -> JSONResponse:
        details = [
            {
                "field": ".".join(str(part) for part in err.get("loc", [])[1:]),
                "message": err.get("msg", ""),
            }
            for err in exc.errors()
        ]
        first = details[0] if details else None
        message = f"{first['field']}: {first['message']}" if first else "参数校验失败"
        return JSONResponse(status_code=200, content=_body(42200, message, details))

    @app.exception_handler(StarletteHTTPException)
    async def handle_http(_: Request, exc: StarletteHTTPException) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content=_body(exc.status_code * 100, str(exc.detail)),
        )

    @app.exception_handler(Exception)
    async def handle_unknown(request: Request, exc: Exception) -> JSONResponse:
        logger.exception("未捕获异常 %s %s", request.method, request.url.path)
        return JSONResponse(
            status_code=500,
            content=_body(50000, "服务器内部错误"),
        )
