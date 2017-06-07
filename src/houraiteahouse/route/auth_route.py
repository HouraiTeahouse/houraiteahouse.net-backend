import json
import logging
from flask import request, Blueprint
from sqlalchemy.exc import IntegrityError
from ..common import bcrypt
from ..bl import auth_bl
from ..bl.auth_bl import authenticate, authorize
from ..storage import auth_storage, models
from ..storage.models import db
from . import request_util
from .request_util import handle_request_errors

auth = Blueprint('auth', __name__)


@auth.route('/register', methods=['POST'])
@handle_request_errors('Registration')
def register():
    json_data = request.data

    try:
        auth_storage.create_user(json_data['email'], json_data['username'],
                                 json_data['password'])
    except IntegrityError:
        return request_util.generate_error_response(400,
            'A user with this name or email already exists.'
        )
    return request_util.generate_success_response('success', 'plain/text')


@auth.route('/login', methods=['POST'])
@handle_request_errors('Login')
def login():
    json_data = request.data
    if 'remember_me' not in json_data:
        json_data['remember_me'] = False

    sessionData = auth_bl.start_user_session(
        json_data['username'],
        json_data['password'],
        json_data['remember_me']
    )

    if sessionData:
        return request_util.generate_success_response(
            json.dumps(sessionData),
            'application/json'
        )

    return request_util.generate_error_response(
        401,
        'Invalid username or password'
    )


@auth.route('/logout', methods=['POST'])
@authenticate
@handle_request_errors('Logout')
def logout():
    json_data = request.data
    # Decorator has already confirmed login
    auth_bl.close_user_session(json_data['session_id'])

    return request_util.generate_success_response(
        'Logout Successful',
        'plain/text'
    )


@auth.route('/status', methods=['GET'])
@handle_request_errors('Fetching login status')
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
        json.dumps(response),
        'application/json'
    )


@auth.route('/update', methods=['POST'])
@authenticate
@handle_request_errors('Updating password')
def change_password():
    json_data = request.data

    if auth_bl.change_password(
        json_data['username'],
        json_data['oldPassword'],
        json_data['newPassword']
    ):

        return request_util.generate_success_response(
            'Update successful',
            'plain/text'
        )

    else:
        return request_util.generate_error_response(
            400,
            'Current password is incorrect.'
        )


# Can only be used by True Administrators

@auth.route('/permissions/<username>', methods=['GET'])
@authorize('admin')
@handle_request_errors('Loading user permissions')
def get_user_permissions(username):
    permissions = auth_storage.get_permissions_by_username(username)

    if permissions is None:
        return request_util.generate_error_response(
            400,
            'User not found!'
        )

    ret = dict()
    ret['username'] = username
    ret['permissions'] = permissions

    return request_util.generate_success_response(
        json.dumps(ret),
        'application/json'
    )


@auth.route('/permissions/<username>', methods=['POST', 'PUT'])
@authorize('admin')
@handle_request_errors('Updating user permissions')
def set_user_permissions(username):
    json_data = request.data

    success = auth_storage.set_permissions_by_username(
        username,
        json_data['permissions'],
        json_data['session_id']
    )

    if success:
        return request_util.generate_success_response(
            'Permissions updated.',
            'plain/text'
        )

    else:
        return request_util.generate_error_response(
            400,
            'You do not have permission to set this user\'s permission.'
        )
