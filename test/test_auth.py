import unittest
from test_util import HouraiTeahouseTestCase

class AuthTest(HouraiTeahouseTestCase):

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
        self.register('ad@min', 'admin', 'password')
        response = self.login('admin','password')
        self.assert200(response)

    def test_login_with_unregistered_user_fails(self):
        response = self.login('admin','admin')
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

    def test_update_can_succeed(self):
        session = self.register_and_login('admin', 'password')
        response = self.client.post('/auth/update', data={
                'username': 'admin',
                'oldPassword': 'password',
                'newPassword': 'password3',
                'session_id': session
            })
        self.assert200(response)

    def test_update_fails_if_password_is_incorrect(self):
        session = self.register_and_login('admin', 'password')
        response = self.client.post('/auth/update', data={
                'username': 'admin',
                'oldPassword': 'passowrd2',
                'newPassword': 'password3',
                'session_id': session
            })
        self.assert400(response)

    def test_update_requires_authentication(self):
        response = self.client.post('/auth/update', data={
                'username': 'admin',
                'oldPassword': 'password',
                'newPassword': 'password3',
            })
        self.assert403(response)

    #TODO(james7132): Fix these tests
    # def test_permissions_get_can_succeed(self):
        # session = self.register_and_login('admin', 'password')
        # self.register('user@user', 'user', 'password')
        # response = self.client.get('/auth/permissions/user?session_id='+session)
        # self.assert200(response)

    # def test_permissions_post_can_succeed(self):
        # session = self.register_and_login('admin', 'password')
        # self.register('user@user', 'user', 'password')
        # response = self.client.post('/auth/permissions/user', data= {
                # 'session_id': session,
                # 'translate': True
            # })
        # self.assert200(response)

    def test_permissions_requires_authorization(self):
        self.register('user@user', 'user', 'password')
        response = self.client.get('/auth/permissions/user')
        self.assert403(response)
        response = self.client.post('/auth/permissions/user', data={
                'admin': True
            })
        self.assert403(response)

if __name__ == "__main__":
    unittest.main()
