"""用内存数据库验证推荐排序、候选过滤及发布者权限。"""
import unittest
from datetime import datetime, timedelta

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.core.exceptions import BusinessError, ForbiddenError, NotFoundError
from app.models.category import Category
from app.models.item import Item
from app.models.user import User
from app.services.recommendation_service import recommend_found


class RecommendationTest(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine("sqlite://")
        for table in (User.__table__, Category.__table__, Item.__table__):
            table.create(self.engine)
        self.db = Session(self.engine, expire_on_commit=False)
        self.when = datetime(2026, 11, 20, 12)
        for uid, role in [(1, "user"), (2, "user"), (3, "admin")]:
            self.db.add(User(id=uid, username=f"u{uid}", email=f"u{uid}@example.com",
                             password_hash="unused", role=role, status=1,
                             created_at=self.when, updated_at=self.when))
        for cid in (1, 2):
            self.db.add(Category(id=cid, name=f"类别{cid}", sort_order=cid, is_active=1))
        self.lost = self.add_item(type="lost", publisher_id=1)
        self.db.commit()

    def add_item(self, **overrides):
        data = dict(type="found", publisher_id=2, category_id=1, title="捡到白色保温杯",
                    description="柴犬贴纸，按压杯盖", location="图书馆三楼",
                    status="published", event_time=self.when + timedelta(hours=2),
                    images="", view_count=0, created_at=self.when, updated_at=self.when)
        data.update(overrides)
        row = Item(**data)
        self.db.add(row)
        self.db.flush()
        return row

    def tearDown(self):
        self.db.close()
        self.engine.dispose()

    def results(self):
        return recommend_found(self.db, self.lost.id, self.db.get(User, 1))

    def test_matching_item_ranks_first_and_results_are_limited(self):
        exact = self.add_item()
        for _ in range(4):
            self.add_item(title="白色水杯", description="金属杯身", location="操场")
        rows = self.results()
        self.assertEqual(len(rows), 3)
        self.assertEqual(rows[0]["id"], exact.id)
        self.assertIn("描述相似", rows[0]["reasons"])
        self.assertIn("地点相近", rows[0]["reasons"])
        self.assertNotIn("contact", rows[0])

    def test_filters_non_candidates(self):
        good = self.add_item()
        for override in [dict(status="returned"), dict(status="offline"),
                         dict(type="lost"), dict(publisher_id=1), dict(category_id=2),
                         dict(event_time=self.when - timedelta(days=2)),
                         dict(event_time=self.when + timedelta(days=31))]:
            self.add_item(**override)
        self.assertEqual([row["id"] for row in self.results()], [good.id])

    def test_same_category_alone_is_not_a_match(self):
        self.add_item(title="黑色雨伞", description="木柄折叠遮阳", location="体育场")
        self.assertEqual(self.results(), [])

    def test_location_and_time_can_match_without_text_overlap(self):
        row = self.add_item(title="未知物品", description="请失主核实")
        self.assertEqual(self.results()[0]["id"], row.id)

    def test_non_owner_including_admin_is_denied(self):
        for uid in (2, 3):
            with self.assertRaises(ForbiddenError):
                recommend_found(self.db, self.lost.id, self.db.get(User, uid))

    def test_missing_and_found_source(self):
        with self.assertRaises(NotFoundError):
            recommend_found(self.db, 999, self.db.get(User, 1))
        self.lost.type = "found"
        with self.assertRaises(BusinessError):
            self.results()

    def test_closed_lost_has_no_recommendations(self):
        self.add_item()
        for status in ("returned", "offline"):
            self.lost.status = status
            self.assertEqual(self.results(), [])


if __name__ == "__main__":
    unittest.main()
