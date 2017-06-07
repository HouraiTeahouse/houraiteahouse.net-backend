from json import loads
import unittest
from flask_testing import TestCase
from houraiteahouse.config import TestConfig
from houraiteahouse.app import create_app
from houraiteahouse.storage.models import User, UserPermissions, db
from houraiteahouse.storage import auth_storage


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
        perms = UserPermissions()
        user = User(email, username, password, perms)
        db.session.add(user)
        db.session.add(perms)
        db.session.commit()
        return user

    def login(self, username, password):
        user = auth_storage.get_user(username)
        return auth_storage.new_user_session(user, False)

    def register_and_login(self, username, password):
        user = self.register('{0}@{1}'.format(username, password), username,
                password)
        session = self.login(username, password)
        return session.session_uuid

    def adminify(self, username):
        """
            Finds a user by their username in the database.
            Grants them all permissions.
            Returns the corresponding user object
        """
        user = User.query.filter_by(username=username).first()
        self.assertIsNotNone(user)
        perms = user.permissions
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
