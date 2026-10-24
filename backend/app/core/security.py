"""安全相关工具：密码哈希与 JWT 签发/校验。

对应 Spring Boot 里的 BCryptPasswordEncoder + JwtUtil。
"""
from datetime import datetime, timedelta, timezone

import bcrypt
import jwt

from app.core.config import settings

# bcrypt 只处理前 72 字节，超出部分会被拒绝（4.x 版本会直接抛错）
_BCRYPT_MAX_BYTES = 72


def hash_password(plain: str) -> str:
    """把明文密码转成 bcrypt 哈希。每次调用结果都不同（盐随机）。"""
    raw = plain.encode("utf-8")[:_BCRYPT_MAX_BYTES]
    return bcrypt.hashpw(raw, bcrypt.gensalt()).decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    """校验明文密码与哈希是否匹配。哈希格式异常时返回 False 而不是抛错。"""
    try:
        raw = plain.encode("utf-8")[:_BCRYPT_MAX_BYTES]
        return bcrypt.checkpw(raw, hashed.encode("utf-8"))
    except (ValueError, TypeError):
        return False


def create_access_token(subject: str, extra: dict | None = None) -> str:
    """签发 JWT。subject 一般放用户 ID。"""
    now = datetime.now(timezone.utc)
    payload: dict = {
        "sub": subject,
        "iat": now,
        "exp": now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    }
    if extra:
        payload.update(extra)
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def decode_token(token: str) -> dict:
    """解析 JWT。过期或签名不符会抛 jwt.PyJWTError，由调用方转成业务异常。"""
    return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
