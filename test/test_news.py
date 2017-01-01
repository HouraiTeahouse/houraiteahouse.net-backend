from mock import mock_open, patch
import unittest
from test_util import HouraiTeahouseTestCase
from houraiteahouse.storage.models import db, Language


USERNAME = 'news'


class NewsTest(HouraiTeahouseTestCase):

    def setUp(self):
        HouraiTeahouseTestCase.setUp(self)
        self.session = self.register_and_login(USERNAME, 'password')
        lang = Language('en', 'English')
        db.session.add(lang)
        db.session.commit()

    def post_test_news(self, session_id=None):
        # TODO(james7132): Add file read/write checks
        m = mock_open()
        with patch('{}.open'.format(__name__), m, create=True):
            data = {
                'title': 'Local Man Drinks Mountain Dew',
                'body': 'Test post pls ignore',
                'tags': {
                    'james', 'mountain dew', 'local man'
                }
            }
            if session_id is not None:
                data['session_id'] = session_id
            return self.client.post('/news/post', data=data)

    def test_list_fails_without_language(self):
        response = self.client.get('/news/list')
        self.assert400(response)

    def test_list_fails_on_empty_news(self):
        response = self.client.get('/news/list?language=en')
        self.assert404(response)

    def test_tag_fails_on_empty_tag(self):
        response = self.client.get('/news/tag/test')
        self.assert404(response)

    def test_get_fails_without_language(self):
        response = self.client.get('/news/get/1')
        self.assert400(response)

    def test_get_fails_on_missing_post(self):
        response = self.client.get('/news/get/1?language=en')
        self.assert404(response)

    def test_post(self):
        self.adminify(USERNAME)
        response = self.post_test_news(self.session)
        self.assert200(response)

    def test_post_requires_authentication(self):
        response = self.post_test_news()
        self.assert403(response)

    def test_post_requires_authorization(self):
        response = self.post_test_news(self.session)
        self.assert403(response)

    def test_edit_can_succeed(self):
        self.adminify(USERNAME)
        response = self.post_test_news(self.session)

    def test_edit_fails_on_missing_post(self):
        self.adminify(USERNAME)
        response = self.client.post('/news/edit/1', data={
            'session_id': self.session,
            'title': 'Local Man Drinks Mountain Dew',
            'body': 'Test post pls ignore',
            'tags': {
                'james', 'mountain dew', 'florida man'
            }
        })
        self.assert400(response)

    def test_edit_requires_authentication(self):
        response = self.client.post('/news/edit/1', data={
            'title': 'Local Man Drinks Mountain Dew',
            'body': 'Test post pls ignore',
            'tags': {
                'james', 'mountain dew', 'florida man'
            }
        })
        self.assert403(response)

    def test_edit_requires_authorization(self):
        response = self.client.post('/news/edit/1', data={
            'session_id': self.session,
            'title': 'Local Man Drinks Mountain Dew',
            'body': 'Test post pls ignore',
            'tags': {
                'james', 'mountain dew', 'florida man'
            }
        })
        self.assert403(response)

    def test_translate_requires_authorization(self):
        response = self.client.post('/news/translate/1', data={
            'session_id': self.session
           })
        self.assert403(response)

    def test_translate_requires_authentication(self):
        response = self.client.post('/news/translate/1', data={})
        self.assert403(response)

    def test_comment_post_fails_on_missing_post(self):
        response = self.client.post('/news/comment/post/1', data={
            'session_id': self.session,
            'body': 'Hello World'
        })
        self.assert400(response)

    def test_comment_post_fails_on_missing_post(self):
        response = self.client.post('/news/comment/post/1', data={
            'session_id': self.session,
            'body': 'Hello World'
        })
        self.assert400(response)


if __name__ == "__main__":
    unittest.main()
