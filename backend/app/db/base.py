"""ORM 声明基类。

所有 models 都继承 Base，Alembic 通过 Base.metadata 感知表结构变化。
"""
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass
