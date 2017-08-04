import unittest
from unittest.mock import mock_open, patch
from test_util import HouraiTeahouseTestCase
from houraiteahouse.storage.models import db, Language

USERNAME = 'news'


class NewsTest(HouraiTeahouseTestCase):

    def setUp(self):
        HouraiTeahouseTestCase.setUp(self)
        self.session = self.register_and_login(USERNAME, 'password')
        lang = Language('en_US', 'English')
        db.session.add(lang)
        db.session.commit()

    def post_test_news(self, session_id=None):
        # TODO(james7132): Add file read/write checks
        m = mock_open()
        data = {
            'title': 'Local Man Drinks Mountain Dew',
            'body': 'Test post pls ignore',
            'tags': [
                'james', 'mountain dew', 'local man'
            ]
        }
        with patch('builtins.open', m, create=True):
            return self.post('/news', session=session_id, data=data)

    def test_list_fails_without_language(self):
        response = self.client.get('/news')
        self.assert400(response)

    def test_list_doesnt_fail_on_empty_news(self):
        response = self.client.get('/news?language=en_US')
        self.assert200(response)

    def test_get_fails_without_language(self):
        response = self.client.get('/news/1')
        self.assert400(response)

    def test_get_fails_on_missing_post(self):
        response = self.client.get('/news/1?language=en_US')
        self.assert404(response)

    def test_post(self):
        self.adminify(USERNAME)
        response = self.post_test_news(self.session)
        self.assert200(response)

    def test_post_requires_authentication(self):
        response = self.post_test_news()
        self.assert401(response)

    def test_post_requires_authorization(self):
        response = self.post_test_news(self.session)
        self.assert403(response)

    def test_edit_can_succeed(self):
        self.adminify(USERNAME)
        response = self.post_test_news(self.session)

    def test_edit_fails_on_missing_post(self):
        self.adminify(USERNAME)
        response = self.put(
            '/news/1',
            session=self.session,
            data={
                'title': 'Local Man Drinks Mountain Dew',
                'body': 'Test post pls ignore',
                'tags': [
                    'james', 'mountain dew', 'florida man'
                ]
            })
        self.assert404(response)

    def test_edit_requires_authentication(self):
        response = self.put(
            '/news/1',
            data={
                'title': 'Local Man Drinks Mountain Dew',
                'body': 'Test post pls ignore',
                'tags': [
                    'james', 'mountain dew', 'florida man'
                ]
            })
        self.assert401(response)

    def test_edit_requires_authorization(self):
        response = self.put(
            '/news/1',
            session=self.session,
            data={
                'title': 'Local Man Drinks Mountain Dew',
                'body': 'Test post pls ignore',
                'tags': [
                    'james', 'mountain dew', 'florida man'
                ]
            })
        self.assert403(response)

    def test_translate_requires_authentication(self):
        response = self.put('/news/1/translate')
        self.assert401(response)

    def test_translate_requires_authorization(self):
        response = self.post('/news/1/translate', session=self.session)
        self.assert403(response)

    def test_comment_post_fails_on_missing_post(self):
        response = self.post('/news/1/comment', session=self.session,
                             data={'body': 'Hello World'})
        self.assert404(response)


if __name__ == "__main__":
    unittest.main()
