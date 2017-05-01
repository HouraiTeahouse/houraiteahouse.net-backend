import unittest
from test_util import HouraiTeahouseTestCase


class AuthTest(HouraiTeahouseTestCase):

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

    def test_permissions_get_can_succeed(self):
        session = self.register_and_login('admin', 'password')
        self.adminify('admin')
        self.register('user@user', 'user', 'password')
        response = self.client.get('/auth/permissions/user', data={
                'session_id': session
            })
        self.assert200(response)

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
