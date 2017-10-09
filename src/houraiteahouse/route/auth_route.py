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
    json_data = request.json

    auth_storage.set_permissions_by_username(
        username,
        json_data['permissions'],
    )

    return request_util.generate_success_response(
        'Permissions updated.',
        'plain/text'
    )
