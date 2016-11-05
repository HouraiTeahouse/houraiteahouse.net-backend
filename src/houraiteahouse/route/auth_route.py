import json, logging
from flask import request
from ..app import app, bcrypt, db
from ..bl import auth_bl
from ..bl.auth_bl import authenticate, authorize
from ..storage import auth_storage, models
from . import request_util

# TODO: refactor to remove some code duplication (ie, stub out common
# request logic)

logger = logging.getLogger(__name__)

@app.route('/auth/register', methods=['POST'])
def register():
    json_data = request.data
    if auth_storage.create_user(
            json_data['email'],
            json_data['username'],
            json_data['password']):
        return request_util.generate_success_response('success', 'plain/text')
    return request_util.generate_error_response(
        400, 'A user with this name or email already exists.')


@app.route('/auth/login', methods=['POST'])
def login():
    json_data = request.data
    if 'remember_me' not in json_data:
        json_data['remember_me'] = False
    try:
        sessionData = auth_bl.start_user_session(
            json_data['username'],
            json_data['password'],
            json_data['remember_me'])
        if sessionData:
            return request_util.generate_success_response(
                json.dumps(sessionData), 'application/json')
        return request_util.generate_error_response(
            401, 'Invalid username or password')
    except:
        return request_util.generate_error_response(
            500, 'Login has failed due to an internal error, '
            'please try again.')


@app.route('/auth/logout', methods=['POST'])
@authenticate
def logout():
    json_data = request.data
    # Decorator has already confirmed login
    auth_bl.close_user_session(json_data['session_id'])
    return request_util.generate_success_response(
        'Logout Successful', 'plain/text')


@app.route('/auth/status', methods=['GET'])
def status():
    json_data = request.args
    if 'session_id' not in json_data:
        response = {'status': False}
    else:
        response = auth_bl.authentication_check(json_data['session_id'])
        if 'permissions' in response:
            permissions = response['permissions']
            permissions.pop('permissions_id')
            # Obscure/hide permissions the user doesn't have
            filteredPerms = {}
            for permission in permissions:
                if permissions[permission]:
                    filteredPerms[permission] = True
            response['permissions'] = filteredPerms
    return request_util.generate_success_response(
        json.dumps(response), 'application/json')


@app.route('/auth/update', methods=['POST'])
@authenticate
def change_password():
    json_data = request.data
    try:
        if auth_bl.change_password(
                json_data['username'],
                json_data['oldPassword'],
                json_data['newPassword']):
            return request_util.generate_success_response(
                'Update successful', 'plain/text')
        else:
            return request_util.generate_error_response(
                400, 'Current password is incorrect.')
    except:
        return request_util.generate_error_response(
            500, 'Failed to update password.  " \
                    "Please try again later.')


# Can only be used by True Administrators

@app.route('/auth/permissions/<username>', methods=['GET'])
@authorize('admin')
def get_user_permissions(username):
    try:
        permissions = auth_storage.get_permissions_by_username(username)
        if permissions is None:
            return request_util.generate_error_response(400,
                                                        'User not found!')
        ret = dict()
        ret['username'] = username
        ret['permissions'] = permissions
        return request_util.generate_success_response(
            json.dumps(ret), 'application/json')
    except:
        return request_util.generate_error_response(
            500, 'Failed to load user permissions." \
            " Please check the server logs')


@app.route('/auth/permissions/<username>', methods=['POST', 'PUT'])
@authorize('admin')
def set_user_permissions(username):
    json_data = request.data
    try:
        success = auth_storage.set_permissions_by_username(
            username, json_data['permissions'], json_data['session_id'])
        if success:
            return request_util.generate_success_response(
                'Permissions updated.', 'plain/text')
        else:
            return request_util.generate_error_response(
                400, 'You do not have permission to set this '
                'user\'s permission.')
    except:
        return request_util.generate_error_response(
            500, 'Failed update user permissions.  '
            'Please check the server logs.')
