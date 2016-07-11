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
        news = data.post_news(request.data['title'], request.data['body'], request.data['tags'])
        if news is None:
            return request_util.generate_error_response(500, 'Failed to create news post')
        return request_util.generate_success_response(json.dumps({'id': news.id}), 'application/json')
    except Exception as e:
        logger.exception('Failed to create news!')
        return request_util.generate_error_response(500, 'Error: {}'.format(e))
