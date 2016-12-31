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

    def test_test(self):
        print(self.db)

if __name__ == "__main__":
    unittest.main()
