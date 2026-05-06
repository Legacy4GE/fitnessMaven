import unittest

from app.auth.passwords import hash_password, verify_password


class TestPasswordHashing(unittest.TestCase):

    def test_hash_returns_bcrypt_string(self):
        hashed = hash_password("mysecretpass")
        self.assertTrue(hashed.startswith("$2b$"))

    def test_hash_is_not_plaintext(self):
        hashed = hash_password("mysecretpass")
        self.assertNotEqual(hashed, "mysecretpass")

    def test_verify_correct_password(self):
        hashed = hash_password("correcthorse")
        self.assertTrue(verify_password("correcthorse", hashed))

    def test_verify_wrong_password(self):
        hashed = hash_password("correcthorse")
        self.assertFalse(verify_password("wrongpassword", hashed))

    def test_different_hashes_for_same_password(self):
        h1 = hash_password("samepass")
        h2 = hash_password("samepass")
        self.assertNotEqual(h1, h2)  # bcrypt salt makes each hash unique


if __name__ == "__main__":
    unittest.main()
