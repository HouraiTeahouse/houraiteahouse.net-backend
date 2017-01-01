from json import loads
import unittest
from flask_testing import TestCase
from houraiteahouse.config import TestConfig
from houraiteahouse.app import create_app
from houraiteahouse.storage.models import db


class HouraiTeahouseTestCase(TestCase):

    def create_app(self):
        self.db = db
        return create_app(TestConfig)

    def setUp(self):
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def assert_error(self, response, error):
        self.assertEqual(response.json, {'message': error})

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

    def adminify(self, username):
        """
            Finds a user by their username in the database.
            Grants them all permissions.
            Returns the corresponding user object
        """
        user = User.query.filter_by(username=username).first()
        self.assertIsNotNone(user)
        perms = user.get_permissions()
        perms.master = True
        perms.admin = True
        perms.team = True
        perms.wiki = True
        perms.news = True
        perms.translate = True
        perms.comment = True

        db.session.merge(perms)
        db.session.commit()
        return user

if __name__ == "__main__":
    unittest.main()
