import unittest
from test_util import HouraiTeahouseTestCase


class RegisterTest(HouraiTeahouseTestCase):

    def test_register_can_succeed(self):
        response = self.register('ad@min', 'admin', 'admin')
        self.assert200(response)

    def test_register_requires_unique_usernames(self):
        self.register('ad@min', 'admin', 'admin')
        response = self.register('test@test', 'admin', 'admin')
        self.assert400(response)
        self.assert_error(response, 'A user with this name or email already '
                          'exists.')

    def test_register_require_unique_emails(self):
        self.register('ad@min', 'admin1', 'password')
        response = self.register('ad@min', 'admin2', 'admin')
        self.assert400(response)
        self.assert_error(response, 'A user with this name or email already '
                          'exists.')

if __name__ == "__main__":
    unittest.main()
