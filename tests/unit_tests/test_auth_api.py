import unittest

from fastapi.testclient import TestClient
from sqlalchemy import create_engine, StaticPool
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.database import Base, get_db


# In-memory SQLite for testing — no PostgreSQL needed
engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestSession = sessionmaker(bind=engine, autocommit=False, autoflush=False)


def override_get_db():
    db = TestSession()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


class AuthAPITestBase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        Base.metadata.create_all(bind=engine)
        cls.client = TestClient(app)

    @classmethod
    def tearDownClass(cls):
        Base.metadata.drop_all(bind=engine)

    def setUp(self):
        # Clear users between tests
        db = TestSession()
        for table in reversed(Base.metadata.sorted_tables):
            db.execute(table.delete())
        db.commit()
        db.close()


class TestRegister(AuthAPITestBase):

    def test_register_success(self):
        resp = self.client.post("/auth/register", json={
            "email": "test@example.com",
            "password": "strongpass123",
            "full_name": "Test User",
        })
        self.assertEqual(resp.status_code, 201)
        data = resp.json()
        self.assertEqual(data["email"], "test@example.com")
        self.assertEqual(data["full_name"], "Test User")
        self.assertTrue(data["is_active"])
        self.assertIn("id", data)
        self.assertNotIn("hashed_password", data)

    def test_register_duplicate_email(self):
        self.client.post("/auth/register", json={
            "email": "dupe@example.com",
            "password": "pass123",
        })
        resp = self.client.post("/auth/register", json={
            "email": "dupe@example.com",
            "password": "pass456",
        })
        self.assertEqual(resp.status_code, 409)

    def test_register_missing_email(self):
        resp = self.client.post("/auth/register", json={
            "password": "pass123",
        })
        self.assertEqual(resp.status_code, 422)


class TestLogin(AuthAPITestBase):

    def _register_user(self):
        self.client.post("/auth/register", json={
            "email": "login@example.com",
            "password": "mypassword",
        })

    def test_login_success(self):
        self._register_user()
        resp = self.client.post("/auth/login", data={
            "username": "login@example.com",
            "password": "mypassword",
        })
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn("access_token", data)
        self.assertIn("refresh_token", data)
        self.assertEqual(data["token_type"], "bearer")

    def test_login_wrong_password(self):
        self._register_user()
        resp = self.client.post("/auth/login", data={
            "username": "login@example.com",
            "password": "wrongpassword",
        })
        self.assertEqual(resp.status_code, 401)

    def test_login_nonexistent_user(self):
        resp = self.client.post("/auth/login", data={
            "username": "nobody@example.com",
            "password": "pass",
        })
        self.assertEqual(resp.status_code, 401)


class TestProtectedRoutes(AuthAPITestBase):

    def _get_tokens(self):
        self.client.post("/auth/register", json={
            "email": "protected@example.com",
            "password": "mypassword",
        })
        resp = self.client.post("/auth/login", data={
            "username": "protected@example.com",
            "password": "mypassword",
        })
        return resp.json()

    def test_me_with_valid_token(self):
        tokens = self._get_tokens()
        resp = self.client.get("/auth/me", headers={
            "Authorization": f"Bearer {tokens['access_token']}"
        })
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["email"], "protected@example.com")

    def test_me_without_token(self):
        resp = self.client.get("/auth/me")
        self.assertEqual(resp.status_code, 401)

    def test_me_with_invalid_token(self):
        resp = self.client.get("/auth/me", headers={
            "Authorization": "Bearer garbage.token.here"
        })
        self.assertEqual(resp.status_code, 401)

    def test_me_with_refresh_token_rejected(self):
        tokens = self._get_tokens()
        resp = self.client.get("/auth/me", headers={
            "Authorization": f"Bearer {tokens['refresh_token']}"
        })
        self.assertEqual(resp.status_code, 401)


class TestRefresh(AuthAPITestBase):

    def _get_tokens(self):
        self.client.post("/auth/register", json={
            "email": "refresh@example.com",
            "password": "mypassword",
        })
        resp = self.client.post("/auth/login", data={
            "username": "refresh@example.com",
            "password": "mypassword",
        })
        return resp.json()

    def test_refresh_success(self):
        tokens = self._get_tokens()
        resp = self.client.post("/auth/refresh", json={
            "refresh_token": tokens["refresh_token"],
        })
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn("access_token", data)
        self.assertIn("refresh_token", data)

    def test_refresh_with_access_token_rejected(self):
        tokens = self._get_tokens()
        resp = self.client.post("/auth/refresh", json={
            "refresh_token": tokens["access_token"],
        })
        self.assertEqual(resp.status_code, 401)

    def test_refresh_with_invalid_token(self):
        resp = self.client.post("/auth/refresh", json={
            "refresh_token": "not.valid.token",
        })
        self.assertEqual(resp.status_code, 401)


class TestLogout(AuthAPITestBase):

    def test_logout(self):
        resp = self.client.post("/auth/logout")
        self.assertEqual(resp.status_code, 200)


if __name__ == "__main__":
    unittest.main()
