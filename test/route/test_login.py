import unittest
from test_util import HouraiTeahouseTestCase


class LoginTest(HouraiTeahouseTestCase):

    def test_login_requires_registration(self):
        self.register('ad@min', 'admin', 'password')
        response = self.login('admin', 'password')
        self.assert200(response)

    def test_login_with_unregistered_user_fails(self):
        response = self.login('admin', 'admin')
        self.assert401(response)
        self.assert_error(response, 'Invalid username or password')

    def test_logout_can_succeed(self):
        session = self.register_and_login('admin', 'password')
        response = self.client.post('/auth/logout', data={
            'session_id': session
        })
        self.assert200(response)
        self.assertIn('Logout Successful', str(response.data))

    def test_logout_fails_when_not_logged_in(self):
        response = self.client.post('/auth/logout', data={
            'session_id': "hello"
        })
        self.assert403(response)

if __name__ == "__main__":
    unittest.main()
