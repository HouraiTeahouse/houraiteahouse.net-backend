import json
import logging

from flask import Flask, request
from houraiteahouse.app import app
from houraiteahouse.bl.auth_bl import authorize
from houraiteahouse.storage import news_storage
from . import request_util

logger = logging.getLogger(__name__)


# TODO: refactor to remove code duplication


@app.route('/news/list', methods=['GET'])
def list_news():
    try:
        news = news_storage.list_news(request.args['language'])
        if news is None:
            return request_util.generate_error_response(404, 'No news found!')
        return request_util.generate_success_response(
            json.dumps(news), 'application/json')
    except Exception as e:
        logger.exception('List news failed: {0}'.format(e))
        return request_util.generate_error_response(
            500, 'Error: {0}'.format(e))


@app.route('/news/tag/get/<tagName>', methods=['GET'])
def get_tag(tagName):
    try:
        news = news_storage.tagged_news(tagName)
        if news is None:
            return request_util.generate_error_response(404, 'No news found!')
        return request_util.generate_success_response(
            json.dumps(news), 'application/json')
    except Exception as e:
        logger.exception('List news for tag failed: {0}'.format(e))
        return request_util.generate_error_response(
            500, 'Error: {0}'.format(e))


@app.route('/news/get/<postId>', methods=['GET'])
def get_news(postId):
    callerSess = None
    if 'session_id' in request.args:
        callerSess = request.args['session_id']
    try:
        news = news_storage.get_news(postId, callerSess, request.args['language'])
        if news is None:
            return request_util.generate_error_response(404, 'Not found!')
        return request_util.generate_success_response(
            json.dumps(news), 'application/json')
    except Exception as e:
        logger.exception('Failed to fetch news: {0}'.format(e))
        return request_util.generate_error_response(
            500, 'Error: {0}'.format(e))


@app.route('/news/post', methods=['PUT', 'POST'])
@authorize('news')
def create_news():
    try:
        media = None if 'media' not in request.data else request.data['media']
        news = news_storage.post_news(
            request.data['title'],
            request.data['body'],
            request.data['tags'],
            request.data['session_id'],
            media)
        if news is None:
            return request_util.generate_error_response(
                500, 'Failed to create news post')
        return request_util.generate_success_response(
            json.dumps({'post_id': news.post_id}), 'application/json')
    except Exception as e:
        logger.exception('Failed to create news: {0}'.format(e))
        return request_util.generate_error_response(
            500, 'Error: {0}'.format(e))


@app.route('/news/edit/<postId>', methods=['PUT', 'POST'])
@authorize('news')
def edit_news(postId):
    try:
        media = None if 'media' not in request.data else request.data['media']
        news = news_storage.edit_news(
            postId,
            request.data['title'],
            request.data['body'],
            request.data['session_id'],
            media)
        if news is None:
            return request_util.generate_error_response(
                400, 'Unknown news post')
        return request_util.generate_success_response(
            json.dumps(news), 'application/json')
    except Exception as e:
        logger.exception('Failed to edit post: {0}'.format(e))
        return request_util.generate_error_response(
            500, 'Error: {0}'.format(e))


@app.route('/news/translate/<postId>', methods=['PUT', 'POST'])
@authorize('translate')
def translate_news(postId):
    try:
        isNew = news_storage.translate_news(
            postId,
            request.data['language'],
            request.data['title'],
            request.data['body'])
        if(isNew is None):
            return request_util.generate_error_response(
                404, 'Cannot submit translation: post not found')
        return request_util.generate_success_response(
            'Translation successfully ' +
            ('created' if isNew else 'updated'),
            'plain/text')
    except Exception as e:
        logger.exception('Failed to post translation: {0}'.format(e))
        return request_util.generate_error_response(
            500, 'Error: {0}'.format(e))


@app.route('/news/comment/post/<postId>', methods=['PUT', 'POST'])
@authorize('comment')
def create_comment(postId):
    try:
        comment = news_storage.post_comment(
            postId,
            request.data['body'],
            request.data['session_id'])
        if comment is None:
            return request_util.generate_error_response(
                400, 'Unknown news post')
        return request_util.generate_success_response(
            json.dumps(comment), 'application/json')
    except Exception as e:
        logger.exception('Failed to create comment: {0}'.format(e))
        return request_util.generate_error_response(
            500, 'Error: {0}'.format(e))


@app.route('/news/comment/edit/<commentId>', methods=['PUT', 'POST'])
@authorize('comment')
def edit_comment(commentId):
    try:
        comment = news_storage.edit_comment(
            commentId,
            request.data['body'],
            request.data['session_id'])
        if comment is None:
            return request_util.generate_error_response(400, 'Unknown comment')
        return request_util.generate_success_response(
            json.dumps(comment), 'application/json')
    except PermissionError as e:
        logger.warn('Disallowed edit called: {0}'.format(e))
        return request_util.generate_error_response(
            403, 'You do not have permission to edit this comment.')
    except Exception as e:
        logger.exception('Failed to edit comment: {0}'.format(e))
        return request_util.generate_error_response(
            500, 'Error: {0}'.format(e))


@app.route('/news/comment/delete/<commentId>', methods=['PUT', 'POST'])
@authorize('comment')
def delete_comment(commentId):
    try:
        if not news_storage.delete_comment(commentId, request.data['session_id']):
            return request_util.generate_error_response(404, 'Unknown comment')
        return request_util.generate_success_response(
            'Comment deleted', 'plain/text')
    except PermissionError as e:
        logger.warn('Disallowed deletion called: {0}'.format(e))
        return request_util.generate_error_response(
            403, 'You do not have permission to delete this comment.')
    except Exception as e:
        logger.exception('Failed to delete comment: {0}'.formate(e))
        return request_util.generate_error_response(
            500, 'Error: {0}'.format(e))
