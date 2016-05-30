import json

from datetime import datetime
from time import time
from sys import exc_info
from flask import Flask, request
from . import data
from .. import request_util
from houraiteahouse.app import app

@app.route('/news', methods=['GET'])
def list_news():
    try:
        news = data.list_news()
        if news is None:
            return request_util.generate_error_response(404, 'No news found!')
        return request_util.generate_success_response(json.dumps(news), 'application/json')
    except:
        e = exc_info()[0]
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
