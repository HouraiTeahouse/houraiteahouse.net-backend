import unittest
from test_util import HouraiTeahouseTestCase


class AuthTest(HouraiTeahouseTestCase):

    def test_register_can_succeed(self):
        response = self.post('/user', data={
            'email': 'ad@min',
            'username': 'admin',
            'password': 'admin'
        })
        self.assert200(response)

    def test_register_requires_unique_usernames(self):
        self.register('ad@min', 'admin', 'admin')
        response = self.post('/user', data={
            'email': 'test@test',
            'username': 'admin',
            'password': 'admin'
        })
        self.assert400(response)

    def test_register_require_unique_emails(self):
        self.register('ad@min', 'admin1', 'password')
        response = self.post('/user', data={
            'email': 'ad@min',
            'username': 'admin2',
            'password': 'admin'
        })
        self.assert400(response)

    def test_login_requires_registration(self):
        self.register('ad@min', 'admin', 'password')
        response = self.post('/user/login', {
            'username': 'admin',
            'password': 'password'
        })
        self.assert200(response)

    def test_login_with_unregistered_user_fails(self):
        response = self.post('/user/login', data={
            'username': 'admin',
            'password': 'admin'
        })
        self.assert401(response)

    def test_logout_can_succeed(self):
        session = self.register_and_login('admin', 'password')
        response = self.post('/user/logout', data={
            'session_id': session
        })
        self.assert200(response)
        self.assertIn('Logout Successful', str(response.data))

    def test_logout_fails_when_not_logged_in(self):
        response = self.post('/user/logout', data={
            'session_id': "hello"
        })
        self.assert401(response)

    def test_update_can_succeed(self):
        session = self.register_and_login('admin', 'password')
        response = self.put('/user/admin', data={
            'oldPassword': 'password',
            'newPassword': 'password3',
            'session_id': session
        })
        self.assert200(response)

    def test_update_fails_if_password_is_incorrect(self):
        session = self.register_and_login('admin', 'password')
        response = self.put('/user/admin', data={
            'username': 'admin',
            'oldPassword': 'passowrd2',
            'newPassword': 'password3',
            'session_id': session
        })
        self.assert401(response)

    def test_update_requires_authentication(self):
        response = self.put('/user/admin', data={
            'username': 'admin',
            'oldPassword': 'password',
            'newPassword': 'password3',
        })
        self.assert401(response)

    def test_get_permissions_can_succeed(self):
        session = self.register_and_login('admin', 'password')
        self.adminify('admin')
        self.register('user@user', 'test_user', 'password')
        response = self.get('/user/test_user/permissions', session=session)
        self.assert200(response)

    def test_put_permissions_can_succeed(self):
        session = self.register_and_login('admin', 'password')
        self.adminify('admin')
        self.register('user@user', 'test_user', 'password')
        response = self.put('/user/test_user/permissions',
                            session=session,
                            data={
                                "permissions": {
                                    'team': True
                                }
                            })
        self.assert200(response)

    def test_get_permissions_requires_authentication(self):
        self.register('user@user', 'test_user', 'password')
        response = self.get('/user/test_user/permissions')
        self.assert401(response)

    def test_put_permissions_requires_authentication(self):
        self.register('user@user', 'test_user', 'password')
        response = self.put('/user/test_user/permissions', data={
            "permissions": {
                'team': True
            }
        })
        self.assert401(response)

    def test_get_permissions_requires_authorization(self):
        self.register('user@user', 'test_user', 'password')
        self.adminify('test_user')
        response = self.get('/user/test_user/permissions')
        self.assert401(response)


if __name__ == "__main__":
    unittest.main()
