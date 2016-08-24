import json
import logging

from datetime import datetime
from time import time
from sys import exc_info
from flask import Flask, request
from houraiteahouse.auth.auth import authorize
from houraiteahouse.app import app
from .. import request_util
from . import data

logger = logging.getLogger(__name__)


@app.route('/news', methods=['GET'])
def list_news():
    try:
        news = data.list_news()
        if news is None:
            return request_util.generate_error_response(404, 'No news found!')
        return request_util.generate_success_response(json.dumps(news), 'application/json')
    except Exception as e:
        logger.exception('List news failed!')
        return request_util.generate_error_response(500, 'Error: {}'.format(e))


@app.route('/tags/<tagName>', methods=['GET'])
def get_tag(tagName):
    try:
        news = data.tagged_news(tagName)
        if news is None:
            return request_util.generate_error_response(404, 'No news found!')
        return request_util.generate_success_response(json.dumps(news), 'application/json')
    except Exception as e:
        logger.exception('List news failed!')
        return request_util.generate_error_response(500, 'Error: {}'.format(e))    


@app.route('/news/<postId>', methods=['GET'])
def get_news(postId):
    try:
        news = data.get_news(postId)
        if news is None:
            return request_util.generate_error_response(404, 'Not found!')
        return request_util.generate_success_response(json.dumps(news), 'application/json')
    except:
        e = exc_info()[0]
        return request_util.generate_error_response(500, 'Error: {}'.format(e))


@authorize('news')
@app.route('/news', methods=['PUT', 'POST'])
def create_news():
    try:
        media = None if not 'media' in request.data else request.data['media']
        news = data.post_news(request.data['title'], request.data['body'], request.data['tags'], request.data['session_id'], media)
        if news is None:
            return request_util.generate_error_response(500, 'Failed to create news post')
        return request_util.generate_success_response(json.dumps({'post_id': news.post_id}), 'application/json')
    except Exception as e:
        logger.exception('Failed to create news!')
        return request_util.generate_error_response(500, 'Error: {}'.format(e))

@authorize('comment')
@app.route('/comment/<postId>', methods=['PUT', 'POST'])
def create_comment(postId):
    try:
        comment = data.post_comment(postId, request.data['body'], request.data['session_id'])
        if comment is None:
            return request_util.generate_error_response(400, 'Unknown news post')
        return request_util.generate_success_response(json.dumps(comment), 'application/json')
    except Exception as e:
        logger.exception('Failed to create comment!')
        return request_util.generate_error_response(500, 'Error: {}'.format(e))
    