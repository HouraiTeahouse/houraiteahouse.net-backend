import json
import logging

from flask import Flask, request
from houraiteahouse.app import app
from houraiteahouse.bl.auth_bl import authorize
from houraiteahouse.storage import news_storage
from . import request_util
from .request_util import handle_request_errors, require_language


logger = logging.getLogger(__name__)


@app.route('/news/list', methods=['GET'])
@require_language('args', 'fetching news')
@handle_request_errors('Fetching news', 'Fetching news list')
def list_news():
    news = news_storage.list_news(request.args['language'])

    if news is None:
        return request_util.generate_error_response(
            404,
            'No news found.'
        )

    return request_util.generate_success_response(
        json.dumps(news),
        'application/json'
    )


@app.route('/news/tag/get/<tag_name>', methods=['GET'])
def get_tag_wrapper(tag_name):
    @require_language('args',
                      'fetching news tagged with \'{0}\''
                      .format(tag_name))
    @handle_request_errors('Fetching news tagged with \'{0}\''
                           .format(tag_name))
    def get_tag(tag_name):
        news = news_storage.tagged_news(
            tag_name,
            request.args['language']
        )

        if news is None:
            return request_util.generate_error_response(
                404,
                'No news found for tag {0}.'.format(tag_name)
            )

        return request_util.generate_success_response(
            json.dumps(news),
            'application/json'
        )

    return get_tag(tag_name)


@app.route('/news/get/<post_id>', methods=['GET'])
def get_news_wrapper(post_id):
    @require_language('args', 'fetching news post {0}'
                      .format(post_id))
    @handle_request_errors('Fetching news post {0}'
                           .format(post_id), 'Fetching full news post')
    def get_news(post_id):
        callerSess = None
        if 'session_id' in request.args:
            callerSess = request.args['session_id']

        news = news_storage.get_news(
            post_id, callerSess, request.args['language'])

        if news is None:
            return request_util.generate_error_response(
                404,
                'Not found!'
            )

        return request_util.generate_success_response(
            json.dumps(news),
            'application/json'
        )

    return get_news(post_id)


@app.route('/news/post', methods=['PUT', 'POST'])
@authorize('news')
@handle_request_errors('Creating news', 'Posting news')
def create_news():
    media = None if 'media' not in request.data else request.data['media']

    news = news_storage.post_news(
        request.data['title'],
        request.data['body'],
        request.data['tags'],
        request.data['session_id'],
        media
    )

    if news is None:
        return request_util.generate_error_response(
            500,
            'Failed to create news post'
        )

    return request_util.generate_success_response(
        json.dumps(
            {
                'post_id': news.post_id
            }
        ),
        'application/json'
    )


@app.route('/news/edit/<post_id>', methods=['PUT', 'POST'])
@authorize('news')
def edit_news_wrapper(post_id):
    @handle_request_errors('Editing news post \'{0}\''
                           .format(post_id),
                           'Posting edit')
    def edit_news(post_id):
        media = None if 'media' not in request.data else request.data['media']

        news = news_storage.edit_news(
            post_id,
            request.data['title'],
            request.data['body'],
            request.data['session_id'],
            media
        )

        if news is None:
            return request_util.generate_error_response(
                400,
                'Unknown news post'
            )

        return request_util.generate_success_response(
            json.dumps(news),
            'application/json'
        )

    return edit_news(post_id)


@app.route('/news/translate/<post_id>', methods=['PUT', 'POST'])
@authorize('translate')
def translate_news_wrapper(post_id):
    @require_language('data', 'translating post \'{0}\''.format(post_id))
    @handle_request_errors('Posting translation of \'{0\''
                           .format(post_id),
                           'Posting translation')
    def translate_news(post_id):
        isNew = news_storage.translate_news(
            post_id,
            request.data['language'],
            request.data['title'],
            request.data['body']
        )

        if isNew is None:
            return request_util.generate_error_response(
                404,
                'Cannot submit translation: post not found'
            )

        return request_util.generate_success_response(
            'Translation successfully ' +
            ('created' if isNew else 'updated'),
            'plain/text'
        )

    return translate_news(post_id)


@app.route('/news/comment/post/<post_id>', methods=['PUT', 'POST'])
@authorize('comment')
def create_comment_wrapper(post_id):
    @handle_request_errors('Posting comment on \'{0}\''
                           .format(post_id),
                           'Posting comment')
    def create_comment(post_id):
        comment = news_storage.post_comment(
            post_id,
            request.data['body'],
            request.data['session_id']
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

    return create_comment(post_id)


@app.route('/news/comment/edit/<comment_id>', methods=['PUT', 'POST'])
@authorize('comment')
def edit_comment_wrapper(comment_id):
    @handle_request_errors('Editing comment \'{0}\''
                           .format(comment_id),
                           'Editing comment')
    def edit_comment(comment_id):
        try:
            comment = news_storage.edit_comment(
                comment_id,
                request.data['body'],
                request.data['session_id']
            )

            if comment is None:
                return request_util.generate_error_response(
                    400,
                    'Unknown comment'
                )

            return request_util.generate_success_response(
                json.dumps(comment),
                'application/json'
            )

        except PermissionError as e:
            logger.warn(
                'Disallowed edit called on {0}: {1}'.format(comment_id, e))
            return request_util.generate_error_response(
                403,
                'You do not have permission to edit this comment.'
            )

    return edit_comment(comment_id)


@app.route('/news/comment/delete/<comment_id>', methods=['PUT', 'POST'])
@authorize('comment')
def delete_comment_wrapper(comment_id):
    @handle_request_errors('Deleting comment \'{0}\''
                           .format(comment_id),
                           'Deleting comment')
    def delete_comment(comment_id):
        try:
            success = news_storage.delete_comment(
                comment_id,
                request.data['session_id']
            )

            if not success:
                return request_util.generate_error_response(
                    404,
                    'Unknown comment'
                )
            return request_util.generate_success_response(
                'Comment deleted',
                'plain/text'
            )

        except PermissionError as e:
            logger.warn('Disallowed deletion called: {0}'.format(e))
            return request_util.generate_error_response(
                403,
                'You do not have permission to delete this comment.'
            )

    return delete_comment(comment_id)
