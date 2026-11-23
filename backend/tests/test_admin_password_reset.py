"""使用内存数据库测试管理员重置密码，不修改开发数据库。"""
import unittest
import asyncio
from datetime import datetime

import httpx
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.security import create_access_token, hash_password, verify_password
from app.db.session import get_db
from app.main import create_app
from app.models.user import User


class AdminPasswordResetTest(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine(
            "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
        )
        User.__table__.create(self.engine)
        self.session = sessionmaker(bind=self.engine, expire_on_commit=False)
        with self.session() as db:
            for user_id, role, status in [(1, "admin", 1), (2, "user", 1), (3, "user", 0)]:
                db.add(User(
                    id=user_id, username=f"test{user_id}", email=f"test{user_id}@example.com",
                    password_hash=hash_password("original123"), role=role, status=status,
                    created_at=datetime.now(), updated_at=datetime.now(),
                ))
            db.commit()

        def override_db():
            with self.session() as db:
                yield db

        app = create_app()
        app.dependency_overrides[get_db] = override_db
        self.app = app

    def tearDown(self):
        self.engine.dispose()

    def post(self, path, **kwargs):
        async def request():
            async with httpx.AsyncClient(
                transport=httpx.ASGITransport(app=self.app), base_url="http://test"
            ) as client:
                return (await client.post(path, **kwargs)).json()
        return asyncio.run(request())

    def reset(self, target=2, operator=1):
        headers = {} if operator is None else {
            "Authorization": f"Bearer {create_access_token(str(operator))}"
        }
        return self.post(
            f"/api/v1/admin/users/{target}/reset-password", headers=headers
        )

    def test_reset_stores_hash_and_changes_login_password(self):
        result = self.reset()
        self.assertEqual(result["code"], 20000)
        self.assertNotIn("password_hash", result["data"])
        with self.session() as db:
            user = db.get(User, 2)
            self.assertNotEqual(user.password_hash, "usr123")
            self.assertTrue(verify_password("usr123", user.password_hash))
            self.assertFalse(verify_password("original123", user.password_hash))
            self.assertTrue(verify_password("original123", db.get(User, 1).password_hash))
        for password, expected in [("usr123", 20000), ("original123", 40000)]:
            result = self.post("/api/v1/auth/login", json={
                "username": "test2", "password": password
            })
            self.assertEqual(result["code"], expected)

    def test_anonymous_and_non_admin_cannot_reset(self):
        for operator, code in [(None, 40100), (2, 40300), (3, 40100)]:
            self.assertEqual(self.reset(operator=operator)["code"], code)
        with self.session() as db:
            self.assertTrue(verify_password("original123", db.get(User, 2).password_hash))

    def test_missing_user(self):
        self.assertEqual(self.reset(target=999)["code"], 40400)

    def test_reset_admin_and_disabled_user(self):
        for target in [1, 3]:
            self.assertEqual(self.reset(target=target)["code"], 20000)
        with self.session() as db:
            self.assertEqual(db.get(User, 3).status, 0)
            self.assertEqual(db.get(User, 1).role, "admin")


if __name__ == "__main__":
    unittest.main()
