import json
import logging
from flask import request, Blueprint
from flask_jwt import jwt_required
from sqlalchemy.exc import IntegrityError
from ..common import bcrypt
from ..bl import auth_bl
from ..bl.auth_bl import authorize
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
    :return: Success response if registration succeeds, Error response
      otherwise
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
@jwt_required()
def change_password():
    """
    Entry point for a logged in user changing their password.
    This is not the entry point for a password reset.
    request data should contain username and both old & new password
    :return: Success response on successful password change, Error response
      otherwise
    :rtype: flask.Response
    """
    json_data = request.json

    auth_bl.change_password(
        json_data['oldPassword'],
        json_data['newPassword']
    )

    return request_util.generate_success_response(
                        'Update successful',
                        'plain/text'
                    )


@user.route('/status', methods=['GET'])
@jwt_required()
def status():
    """
    Entry point for checking status of current user session
    request data should contain the session_id we want the status of
    :return: Success response containing permissions blob if session is valid,
      else False
    :rtype: flask.Response
    """
    json_data = request.args

    response = auth_bl.authentication_check()

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
    :return: Success response containing username & permissions on successful
      authZ & lookup, Error response otherwise
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
    :return: Success response in raw text encoding on successful authZ &
      update, Error response otherwise
    :rtype: flask.Response
    """
    json_data = request.json

    auth_storage.set_permissions_by_username(
        username,
        json_data['permissions'],
    )

    return request_util.generate_success_response(
        'Permissions updated.',
        'plain/text'
    )
