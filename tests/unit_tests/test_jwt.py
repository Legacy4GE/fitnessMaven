import unittest
from unittest.mock import patch
from datetime import datetime, timedelta, timezone

from app.auth.jwt import create_access_token, create_refresh_token, decode_token


class TestAccessToken(unittest.TestCase):

    def test_create_and_decode(self):
        token = create_access_token("user-123")
        payload = decode_token(token)
        self.assertEqual(payload["sub"], "user-123")
        self.assertEqual(payload["type"], "access")

    def test_expiry_is_set(self):
        token = create_access_token("user-123")
        payload = decode_token(token)
        self.assertIn("exp", payload)

    def test_invalid_token_returns_none(self):
        result = decode_token("not.a.valid.token")
        self.assertIsNone(result)

    def test_expired_token_returns_none(self):
        with patch("app.auth.jwt.datetime") as mock_dt:
            mock_dt.now.return_value = datetime(2020, 1, 1, tzinfo=timezone.utc)
            mock_dt.side_effect = lambda *a, **kw: datetime(*a, **kw)
            token = create_access_token("user-123")
        # Token was created with a 2020 expiry, so it's expired now
        result = decode_token(token)
        self.assertIsNone(result)


class TestRefreshToken(unittest.TestCase):

    def test_create_and_decode(self):
        token = create_refresh_token("user-456")
        payload = decode_token(token)
        self.assertEqual(payload["sub"], "user-456")
        self.assertEqual(payload["type"], "refresh")

    def test_refresh_token_different_from_access(self):
        access = create_access_token("user-789")
        refresh = create_refresh_token("user-789")
        self.assertNotEqual(access, refresh)


if __name__ == "__main__":
    unittest.main()
