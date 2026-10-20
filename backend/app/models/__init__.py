"""ORM 模型包。

新增模型后必须在这里导入一次，否则 Alembic 自动生成迁移时看不到这张表。
导入顺序也有讲究：被引用的表要先导入，否则 relationship 解析不到类名。
"""
from app.models.category import Category
from app.models.user import User
from app.models.item import Item
from app.models.claim import Claim
from app.models.notice import Notice

__all__ = ["User", "Category", "Item", "Claim", "Notice"]
