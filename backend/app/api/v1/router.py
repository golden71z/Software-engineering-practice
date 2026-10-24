"""v1 路由聚合。

新增模块（items / claims / categories / admin）时只在这里 include 一行。
"""
from fastapi import APIRouter

from app.api.v1 import admin, auth, categories, claims, health, items, notices, upload

api_router = APIRouter()

api_router.include_router(health.router)
api_router.include_router(auth.router, prefix="/auth")
api_router.include_router(categories.router, prefix="/categories")
api_router.include_router(items.router, prefix="/items")
api_router.include_router(claims.router, prefix="/claims")
api_router.include_router(notices.router, prefix="/notices")
api_router.include_router(upload.router, prefix="/upload")
api_router.include_router(admin.router, prefix="/admin")
