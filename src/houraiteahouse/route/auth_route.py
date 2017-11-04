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

user = Blueprint('user', __name__)


@user.route('', methods=['POST'])
def register():
    """
    Entry point for registering a new user
    request data should contain an email address, username, and password
    :return: Success response if registration succeeds, Error response otherwise
    :rtype: flask.Response
    """
    json_data = request.json

    try:
        auth_storage.create_user(json_data['email'], json_data['username'],
                                 json_data['password'])
    except IntegrityError:
        raise BadRequest(
            'A user with this name or email already exists.') from None
    return request_util.generate_success_response('success', 'plain/text')


@user.route('', methods=['PUT'])
@authenticate
def change_password():
    """
    Entry point for a logged in user changing their password.
    This is not the entry point for a password reset.
    request data should contain username and both old & new password
    :return: Success response on successful password change, Error response otherwise
    :rtype: flask.Response
    """
    json_data = request.json

    auth_bl.change_password(
        json_data['username'],
        json_data['oldPassword'],
        json_data['newPassword']
    )

    return request_util.generate_success_response(
                        'Update successful',
                        'plain/text'
                    )


@user.route('/login', methods=['POST'])
def login():
    """
    Entry point for user login
    request data should contain username, password, and the remember_me flag 
    :return: Success response with session data upon successful login, Error response otherwise
    :rtype: flask.Response
    """
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
    """
    Entry point for user logout
    request data should contain the session_id to close
    :return: Success response
    :rtype: flask.Response
    """
    json_data = request.json
    # Decorator has already confirmed login
    auth_bl.close_user_session(json_data['session_id'])

    return request_util.generate_success_response(
        'Logout Successful',
        'plain/text'
    )


@user.route('/status', methods=['GET'])
def status():
    """
    Entry point for checking status of current user session
    request data should contain the session_id we want the status of
    :return: Success response containing permissions blob if session is valid, else False
    :rtype: flask.Response
    """
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
    """
    Entry point for fetching permissions associated to a given user
    This route requires admin privileges to invoke 
    :param username: User whose permissions will be fetched
    :type username: basestring
    :return: Success response containing username & permissions on successful authZ & lookup, Error response otherwise
    :rtype: flask.Response
    """
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


@user.route('/<username>/permissions', methods=['POST', 'PUT'])
@authorize('admin')
def set_user_permissions(username):
    """
    Entry point for updating permissions of a given user
    request data should contain the new permissions to set
    :param username: User whose permissions will be updated
    :type username: basestring
    :return: Success response in raw text encoding on successful authZ & update, Error response otherwise
    :rtype: flask.Response
    """
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
