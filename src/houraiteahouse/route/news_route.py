import json
import logging

from flask import Flask, request, Blueprint
from houraiteahouse.bl.auth_bl import authorize
from houraiteahouse.storage import news_storage
from . import request_util
from .request_util import require_language

news = Blueprint('news', __name__)
logger = logging.getLogger(__name__)


@news.route('/list', methods=['GET'])
@require_language('args', 'fetching news')
def list_news():
    news = news_storage.list_news(request.args['language'])
    return request_util.generate_success_response(
        json.dumps(news),
        'application/json'
    )


@news.route('/tag/get/<tag_name>', methods=['GET'])
def get_tag_wrapper(tag_name):
    @require_language('args',
                      'fetching news tagged with \'{0}\''
                      .format(tag_name))
    def get_tag(tag_name):
        news = news_storage.tagged_news(
            tag_name,
            request.args['language']
        )

        return request_util.generate_success_response(
            json.dumps(news),
            'application/json'
        )

    return get_tag(tag_name)


@news.route('/get/<post_id>', methods=['GET'])
def get_news_wrapper(post_id):
    @require_language('args', 'fetching news post {0}'
                      .format(post_id))
    def get_news(post_id):
        callerSess = None
        if 'session_id' in request.args:
            callerSess = request.args['session_id']

        news = news_storage.get_news(post_id, callerSess,
                                     request.args['language'])

        return request_util.generate_success_response(
            json.dumps(news),
            'application/json'
        )

    return get_news(post_id)


@news.route('/post', methods=['POST'])
@authorize('news')
def create_news():
    media = None if 'media' not in request.json else request.json['media']
    json_data = request.json
    news = news_storage.post_news(
        json_data['title'],
        json_data['body'],
        json_data['tags'],
        json_data['session_id'],
        media
    )

    return request_util.generate_success_response(
        json.dumps({'post_id': news['post_id']}),
        'application/json'
    )


@news.route('/edit/<post_id>', methods=['PUT'])
@authorize('news')
def edit_news(post_id):
    media = None if 'media' not in request.json else request.json['media']

    news = news_storage.edit_news(
        post_id,
        request.json['title'],
        request.json['body'],
        request.json['session_id'],
        media
    )

    return request_util.generate_success_response(
        json.dumps(news),
        'application/json'
    )


@news.route('/translate/<post_id>', methods=['PUT', 'POST'])
@authorize('translate')
def translate_news_wrapper(post_id):
    @require_language('data', 'translating post \'{0}\''.format(post_id))
    def translate_news(post_id):
        isNew = news_storage.translate_news(
            post_id,
            request.json['language'],
            request.json['title'],
            request.json['body']
        )

        return request_util.generate_success_response(
            'Translation successfully ' +
            ('created' if isNew else 'updated'),
            'plain/text'
        )

    return translate_news(post_id)


@news.route('/comment/post/<post_id>', methods=['POST'])
@authorize('comment')
def create_comment(post_id):
    comment = news_storage.post_comment(
        post_id,
        request.json['body'],
        request.json['session_id']
    )

    if comment is None:
        return request_util.generate_error_response(
            400,
            'Unknown news post'
        )

    return request_util.generate_success_response(
        json.dumps(comment),
        'application/json'
    )


@news.route('/comment/edit/<comment_id>', methods=['PUT'])
@authorize('comment')
def edit_comment(comment_id):
    comment = news_storage.edit_comment(
        comment_id,
        request.json['body'],
        request.json['session_id']
    )

    return request_util.generate_success_response(
        json.dumps(comment),
        'application/json'
    )


@news.route('/comment/delete/<comment_id>', methods=['PUT', 'POST'])
@authorize('comment')
def delete_comment(comment_id):
    success = news_storage.delete_comment(
        comment_id,
        request.json['session_id']
    )

    return request_util.generate_success_response(
        'Comment deleted',
        'plain/text'
    )
