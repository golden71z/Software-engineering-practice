"""个人改密回归测试，仅使用内存数据库。"""
import unittest
from datetime import datetime

from fastapi.security import HTTPAuthorizationCredentials
from pydantic import ValidationError
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.api.v1.auth import change_password as change_password_endpoint
from app.core.exceptions import BusinessError, UnauthorizedError
from app.core.security import create_access_token, hash_password, verify_password
from app.models.user import User
from app.schemas.user import PasswordChange
from app.services import user_service


class ChangePasswordTest(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine("sqlite://")
        User.__table__.create(self.engine)
        self.db = Session(self.engine, expire_on_commit=False)
        for uid, role in [(1, "user"), (2, "admin")]:
            self.db.add(User(
                id=uid, username=f"user{uid}", email=f"user{uid}@example.com",
                password_hash=hash_password("original123"), role=role, status=1,
                created_at=datetime.now(), updated_at=datetime.now(),
            ))
        self.db.commit()

    def tearDown(self):
        self.db.close()
        self.engine.dispose()

    def test_user_and_admin_can_change_only_their_own_password(self):
        for uid in (1, 2):
            credentials = HTTPAuthorizationCredentials(
                scheme="Bearer", credentials=create_access_token(str(uid))
            )
            current = get_current_user(credentials, self.db)
            result = change_password_endpoint(
                PasswordChange(current_password="original123", new_password="changed123"),
                self.db, current,
            )
            self.assertEqual(result.code, 20000)
            self.assertTrue(result.data)
            self.assertNotEqual(current.password_hash, "changed123")
            self.assertTrue(verify_password("changed123", current.password_hash))
            self.assertFalse(verify_password("original123", current.password_hash))
            user_service.login(self.db, current.username, "changed123")
            with self.assertRaises(BusinessError):
                user_service.login(self.db, current.username, "original123")
            if uid == 1:
                self.assertTrue(verify_password("original123", self.db.get(User, 2).password_hash))

    def test_wrong_current_password_does_not_change_hash(self):
        user = self.db.get(User, 1)
        original_hash = user.password_hash
        with self.assertRaisesRegex(BusinessError, "当前密码不正确"):
            user_service.change_password(self.db, user, PasswordChange(
                current_password="wrong123", new_password="changed123"
            ))
        self.assertEqual(user.password_hash, original_hash)

    def test_same_password_rejected(self):
        with self.assertRaisesRegex(BusinessError, "不能与当前密码相同"):
            user_service.change_password(self.db, self.db.get(User, 1), PasswordChange(
                current_password="original123", new_password="original123"
            ))

    def test_invalid_new_password_rejected(self):
        for value in ["", "12345", "a" * 65, "密" * 25]:
            with self.subTest(value=value), self.assertRaises(ValidationError):
                PasswordChange(current_password="original123", new_password=value)

    def test_login_required_and_disabled_account_rejected(self):
        with self.assertRaises(UnauthorizedError):
            get_current_user(None, self.db)
        user = self.db.get(User, 1)
        user.status = 0
        self.db.commit()
        credentials = HTTPAuthorizationCredentials(
            scheme="Bearer", credentials=create_access_token("1")
        )
        with self.assertRaises(UnauthorizedError):
            get_current_user(credentials, self.db)


if __name__ == "__main__":
    unittest.main()
