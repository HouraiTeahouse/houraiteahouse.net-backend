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
from werkzeug.exceptions import NotFound, BadRequest, Unauthorized

user = Blueprint('auth', __name__)


@user.route('', methods=['POST'])
def register():
    json_data = request.json
    try:
        auth_storage.create_user(json_data['email'], json_data['username'],
                                 json_data['password'])
    except IntegrityError:
        raise BadRequest(
            'A user with this name or email already exists.') from None
    return request_util.generate_success_response('success', 'plain/text')


@user.route('/<username>', methods=['PUT'])
@authenticate
def change_password(username):
    json_data = request.json

    auth_bl.change_password(
        username,
        json_data['oldPassword'],
        json_data['newPassword']
    )

    return request_util.generate_success_response(
        'Update successful',
        'plain/text'
    )


@user.route('/login', methods=['POST'])
def login():
    json_data = request.json
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
    raise Unauthorized('Invalid username or password')


@user.route('/logout', methods=['POST'])
@authenticate
def logout():
    json_data = request.json
    # Decorator has already confirmed login
    auth_bl.close_user_session(json_data['session_id'])

    return request_util.generate_success_response(
        'Logout Successful',
        'plain/text'
    )


@user.route('/status', methods=['GET'])
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


# Can only be used by True Administrators

@user.route('/<username>/permissions', methods=['GET'])
@authorize('admin')
def get_user_permissions(username):
    permissions = auth_storage.get_permissions_by_username(username)

    if permissions is None:
        raise NotFound('User not found.')
    return request_util.generate_success_response(
        json.dumps({
            'username': username,
            'permissions': permissions
        }),
        'application/json'
    )


@user.route('/<username>/permissions', methods=['PUT'])
@authorize('admin')
def set_user_permissions(username):
    json_data = request.json

    auth_storage.set_permissions_by_username(
        username,
        json_data['permissions'],
        json_data['session_id']
    )

    return request_util.generate_success_response(
        'Permissions updated.',
        'plain/text'
    )
