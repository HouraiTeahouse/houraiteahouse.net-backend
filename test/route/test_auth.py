
from test_util import HouraiTeahouseTestCase


class AuthTest(HouraiTeahouseTestCase):

    def test_update_can_succeed(self):
        session = self.register_and_login('admin', 'password')
        response = self.put('/auth', data={
            'username': 'admin',
            'oldPassword': 'password',
            'newPassword': 'password3',
            'session_id': session
        })
        self.assert200(response)

    def test_update_fails_if_password_is_incorrect(self):
        session = self.register_and_login('admin', 'password')
        response = self.put('/auth', data={
            'username': 'admin',
            'oldPassword': 'passowrd2',
            'newPassword': 'password3',
            'session_id': session
        })
        self.assert401(response)

    def test_update_requires_authentication(self):
        response = self.put('/auth', data={
            'username': 'admin',
            'oldPassword': 'password',
            'newPassword': 'password3',
        })
        self.assert401(response)

    def test_get_permissions_can_succeed(self):
        session = self.register_and_login('admin', 'password')
        self.adminify('admin')
        self.register('user@user', 'user', 'password')
        response = self.get('/auth/user/permissions', session=session)
        self.assert200(response)

    def test_put_permissions_can_succeed(self):
        session = self.register_and_login('admin', 'password')
        self.adminify('admin')
        self.register('user@user', 'user', 'password')
        response = self.put('/auth/user/permissions',
                            session=session,
                            data={
                                "permissions": {
                                    'team': True
                                }
                            })
        self.assert200(response)

    def test_get_permissions_requires_authentication(self):
        self.register('user@user', 'user', 'password')
        response = self.get('/auth/user/permissions')
        self.assert401(response)

    def test_put_permissions_requires_authentication(self):
        self.register('user@user', 'user', 'password')
        response = self.put('/auth/user/permissions', data={
            "permissions": {
                'team': True
            }
        })
        self.assert401(response)

    def test_get_permissions_requires_authorization(self):
        self.register('user@user', 'user', 'password')
        self.adminify('user')
        response = self.get('/auth/user/permissions')
        self.assert401(response)
        response = self.put('/auth/user/permissions', data={
            'admin': True
        })
        self.assert401(response)


if __name__ == "__main__":
    unittest.main()
