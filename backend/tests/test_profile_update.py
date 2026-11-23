"""个人资料更新测试，不操作开发数据库。"""
import unittest
from datetime import datetime

from pydantic import ValidationError
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.api.v1.auth import update_me
from app.core.exceptions import BusinessError
from app.models.user import User
from app.schemas.user import ProfileUpdate
from app.services.user_service import update_profile


class ProfileUpdateTest(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine("sqlite://")
        User.__table__.create(self.engine)
        self.db = Session(self.engine, expire_on_commit=False)
        for uid, role in [(1, "user"), (2, "admin")]:
            self.db.add(User(id=uid, username=f"user{uid}", email=f"u{uid}@example.com",
                             password_hash="unchanged", role=role, status=1,
                             created_at=datetime.now(), updated_at=datetime.now()))
        self.db.commit()

    def tearDown(self):
        self.db.close()
        self.engine.dispose()

    def test_user_and_admin_can_update_own_profile(self):
        for uid in (1, 2):
            result = update_me(ProfileUpdate(email=f"new{uid}@example.com", real_name=" 张三 ",
                                            phone="13800138000"), self.db, self.db.get(User, uid))
            self.assertEqual(result.code, 20000)
            self.assertEqual(result.data.real_name, "张三")
            self.assertEqual(result.data.email, f"new{uid}@example.com")
            self.assertNotIn("password_hash", result.data.model_dump())
            self.assertEqual(self.db.get(User, uid).password_hash, "unchanged")
            self.assertEqual(self.db.get(User, uid).username, f"user{uid}")
            if uid == 1:
                self.assertEqual(self.db.get(User, 2).email, "u2@example.com")

    def test_duplicate_email_rejected_without_changing_profile(self):
        with self.assertRaises(BusinessError):
            update_profile(self.db, self.db.get(User, 1), ProfileUpdate(
                email="u2@example.com", real_name="不应保存"
            ))
        self.assertEqual(self.db.get(User, 1).email, "u1@example.com")
        self.assertIsNone(self.db.get(User, 1).real_name)

    def test_keep_current_email_and_clear_optional_fields(self):
        user = update_profile(self.db, self.db.get(User, 1), ProfileUpdate(
            email="u1@example.com", phone="  ", real_name="  "
        ))
        self.assertIsNone(user.phone)
        self.assertIsNone(user.real_name)

    def test_invalid_fields_and_privilege_changes_rejected(self):
        for data in [dict(email="invalid"), dict(phone="123"), dict(phone="1380013800"),
                     dict(phone="138001380000"), dict(phone="1380013800a"), dict(real_name="a" * 33),
                     dict(role="admin"), dict(id=2), dict(status=0), dict(username="other")]:
            payload = {"email": "u1@example.com", **data}
            with self.subTest(data=data), self.assertRaises(ValidationError):
                ProfileUpdate(**payload)


if __name__ == "__main__":
    unittest.main()
