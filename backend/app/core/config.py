"""应用配置层。

所有可配置项集中在这里，值从环境变量或 .env 文件读取。
对应 Spring Boot 的 application.yml + @ConfigurationProperties。
"""
from functools import lru_cache
from pathlib import Path
from urllib.parse import quote_plus

from pydantic_settings import BaseSettings, SettingsConfigDict

# 项目根目录（backend/），用于定位 .env
BASE_DIR = Path(__file__).resolve().parent.parent.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(BASE_DIR / ".env"),
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    # ---- 应用 ----
    APP_NAME: str = "校园失物招领管理系统"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = True
    API_V1_PREFIX: str = "/api/v1"

    # ---- 认证 ----
    SECRET_KEY: str = "dev-secret-key-change-me"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440

    # ---- 数据库 ----
    MYSQL_HOST: str = "127.0.0.1"
    MYSQL_PORT: int = 3306
    MYSQL_USER: str = "root"
    MYSQL_PASSWORD: str = ""
    MYSQL_DB: str = "campus_lostfound"
    SQL_ECHO: bool = False

    # ---- 跨域 ----
    CORS_ORIGINS: str = "http://localhost:8090,http://127.0.0.1:8090"

    @property
    def database_url(self) -> str:
        """拼出 SQLAlchemy 连接串，密码做 URL 转义（防止含 @ : / 等字符出错）。"""
        password = quote_plus(self.MYSQL_PASSWORD)
        return (
            f"mysql+pymysql://{self.MYSQL_USER}:{password}"
            f"@{self.MYSQL_HOST}:{self.MYSQL_PORT}/{self.MYSQL_DB}?charset=utf8mb4"
        )

    @property
    def cors_origin_list(self) -> list[str]:
        return [item.strip() for item in self.CORS_ORIGINS.split(",") if item.strip()]


@lru_cache
def get_settings() -> Settings:
    """带缓存的配置读取，保证全应用只实例化一次。"""
    return Settings()


settings = get_settings()
