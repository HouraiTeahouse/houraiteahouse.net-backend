import unittest
from houraiteahouse.storage import auth_storage
from test_util import HouraiTeahouseTestCase


class AuthUserStorageTest(HouraiTeahouseTestCase):

    def test_create_user_can_succeed(self):
        self.assertTrue(auth_storage.create_user("test@test", "test", "test"))

    def test_create_user_requires_unique_username(self):
        self.assertTrue(auth_storage.create_user("test@test", "test", "test"))
        self.assertFalse(auth_storage.create_user("test2@test", "test", "test2"))

    def test_create_user_requires_unique_email(self):
        self.assertTrue(auth_storage.create_user("test@test", "test", "test"))
        self.assertFalse(auth_storage.create_user("test@test", "test2", "test2"))

    def test_create_user_allows_duplicate_passwords(self):
        self.assertTrue(auth_storage.create_user("test@test", "test", "test"))
        self.assertTrue(auth_storage.create_user("test2@test", "test2", "test"))

    def test_get_user_can_succeed(self):
        self.assertTrue(auth_storage.create_user("test@test", "test", "test"))
        self.assertIsNotNone(auth_storage.get_user("test"))

    def test_get_user_fails_if_user_doesnt_exist(self):
        self.assertIsNone(auth_storage.get_user("test"))

    def test_get_user_by_id_can_succeed(self):
        self.assertTrue(auth_storage.create_user("test@test", "test", "test"))
        user_id = 1
        user = auth_storage.get_user_by_id(user_id)
        self.assertIsNotNone(user)
        self.assertEqual(user.user_id, user_id)

    def test_get_user_fails_if_user_doesnt_exist(self):
        self.assertIsNone(auth_storage.get_user(1))

if __name__ == "__main__":
    unittest.main()
