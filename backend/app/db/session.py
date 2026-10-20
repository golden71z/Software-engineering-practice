"""数据库连接与会话管理。

create_engine 是惰性的：只有真正执行 SQL 时才会建立物理连接。
所以数据库暂时连不上时，应用依然可以启动，/docs 和健康检查也能访问。
"""
from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import settings

engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,      # 取连接前先探活，避免拿到已断开的连接
    pool_recycle=3600,       # MySQL 默认 8 小时断开空闲连接，提前回收
    pool_size=5,
    max_overflow=10,
    echo=settings.SQL_ECHO,  # 打开后会在控制台打印每条 SQL
    future=True,
)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False,  # commit 后对象仍可读，避免返回时再查一次库
)


def get_db() -> Generator[Session, None, None]:
    """FastAPI 依赖：每个请求一个独立 Session，请求结束自动关闭。"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
