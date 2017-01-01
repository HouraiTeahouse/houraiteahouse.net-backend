import unittest
from test_util import HouraiTeahouseTestCase


class AuthTest(HouraiTeahouseTestCase):

    def register(self, email, username, password):
        return self.client.post('/auth/register', data={
            'email': email,
            'username': username,
            'password': password
        })

    def login(self, username, password):
        return self.client.post('/auth/login', data={
            'username': username,
            'password': password,
        })

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

    def test_login_requires_registration(self):
        self.register('ad@min', 'admin', 'admin')
        response = self.login('admin', 'admin')
        self.assert200(response)

    def test_login_with_unregistered_user_fails(self):
        response = self.login('admin', 'admin')
        self.assert401(response)
        self.assert_error(response, 'Invalid username or password')


if __name__ == "__main__":
    unittest.main()
