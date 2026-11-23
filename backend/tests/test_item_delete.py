"""删除发布的所有权、关联清理和事务回滚测试。"""
import unittest
from unittest.mock import patch

from sqlalchemy import select, text

from app.core.exceptions import ForbiddenError, NotFoundError
from app.models.claim import Claim
from app.models.favorite import Favorite
from app.models.item import Item
from app.models.user import User
from app.repositories import item_repo
from app.services.item_service import delete_item
from test_recommendations import RecommendationTest


class ItemDeleteTest(unittest.TestCase):
    def setUp(self):
        RecommendationTest.setUp(self)
        self.db.execute(text("PRAGMA foreign_keys=ON"))
        Claim.__table__.create(self.engine)
        Favorite.__table__.create(self.engine)

    tearDown = RecommendationTest.tearDown
    add_item = RecommendationTest.add_item

    def add_related(self):
        self.db.add(Claim(item_id=self.lost.id, applicant_id=2, proof="物品描述足够长",
                          status="pending", created_at=self.when))
        self.db.add(Favorite(item_id=self.lost.id, user_id=2, created_at=self.when))
        self.db.commit()

    def test_owner_can_delete_in_all_statuses(self):
        other = self.add_item()
        self.db.commit()
        for status in ("published", "offline", "returned"):
            row = self.add_item(publisher_id=1, status=status)
            self.db.commit()
            row_id = row.id
            delete_item(self.db, self.db.get(User, 1), row_id)
            self.assertIsNone(self.db.get(Item, row_id))
        self.assertIsNotNone(self.db.get(Item, other.id))

    def test_non_owner_and_admin_cannot_delete_others(self):
        for uid in (2, 3):
            with self.assertRaises(ForbiddenError):
                delete_item(self.db, self.db.get(User, uid), self.lost.id)
        self.assertIsNotNone(self.db.get(Item, self.lost.id))

    def test_missing_item(self):
        with self.assertRaises(NotFoundError):
            delete_item(self.db, self.db.get(User, 1), 999)

    def test_related_records_are_deleted_with_foreign_keys_enabled(self):
        self.add_related()
        item_id = self.lost.id
        delete_item(self.db, self.db.get(User, 1), item_id)
        self.assertIsNone(self.db.get(Item, item_id))
        self.assertEqual(list(self.db.scalars(select(Claim))), [])
        self.assertEqual(list(self.db.scalars(select(Favorite))), [])

    def test_failure_rolls_back_related_deletion(self):
        self.add_related()
        original = item_repo.delete_with_related
        def fail_after_delete(db, item):
            original(db, item)
            raise RuntimeError("simulated failure")
        with patch.object(item_repo, "delete_with_related", side_effect=fail_after_delete):
            with self.assertRaises(RuntimeError):
                delete_item(self.db, self.db.get(User, 1), self.lost.id)
        self.assertIsNotNone(self.db.get(Item, self.lost.id))
        self.assertEqual(len(list(self.db.scalars(select(Claim)))), 1)
        self.assertEqual(len(list(self.db.scalars(select(Favorite)))), 1)


if __name__ == "__main__":
    unittest.main()
