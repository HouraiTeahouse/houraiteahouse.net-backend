import json
from flask import request
from houraiteahouse.app import app, bcrypt, db
from houraiteahouse import models, request_util
from . import auth, data
from .auth import authenticate


@app.route('/auth/register', methods=['POST'])
def register():
    json_data = request.data
    if data.create_user(json_data['email'], json_data['username'], json_data['password']):
        return request_util.generate_success_response('success', 'plain/text')
    return request_util.generate_error_response(400, 'A user with this name or email already exists.')


@app.route('/auth/login', methods=['POST'])
def login():
    json_data = request.data
    try:
        sessionData = auth.start_user_session(json_data['username'], json_data['password'])
        if sessionData is not None:
            return request_util.generate_success_response(json.dumps(sessionData), 'application/json')
        return request_util.generate_error_response(401, 'Invalid username or password')
    except:
        return request_util.generate_error_response(500, 'Login has failed due to an internal error, please try again.')


@authenticate
@app.route('/auth/logout', methods=['POST'])
def logout():
    json_data = request.data
    # Decorator has already confirmed login
    auth.close_user_session(json_data['session_id'])
    return request_util.generate_success_response('Logout Successful', 'plain/text')


@app.route('/auth/status', methods=['GET'])
def status():
    json_data = request.data
    if not 'session_id' in json_data:
        response = False
    else:
        response = auth.authentication_check(json_data['session_id'])
    return request_util.generate_response(200, json.dumps({'status': response}), 'application/json')


@authenticate
@app.route('/auth/update', methods=['POST'])
def change_password():
    json_data = request.data
    try:
        if auth.change_password(json_data['username'], json_data['oldPassword'], json_data['newPassword']):
            return request_util.generate_success_response('Update successful', 'plain/text')
        else:
            return request_util.generate_error_response(400, 'Current password is incorrect.')
    except:
        return request_util.generate_error_response(500, 'Failed to update password.  Please try again later.')
