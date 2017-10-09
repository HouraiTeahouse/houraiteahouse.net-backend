import logging

from datetime import datetime
from flask_sqlalchemy_cache import FromCache
from sqlalchemy import inspect, exc
from houraiteahouse.storage import models
from houraiteahouse.storage import storage_util as util
from houraiteahouse.storage.models import db, cache
from werkzeug.exceptions import Forbidden
from flask_jwt import JWT, current_identity

logger = logging.getLogger(__name__)


def authenticate_user(username, password):
    user = get_user(username)
    if user and user.check_password(password):
        return user


def identify_user(payload):
    user_id = payload['identity']
    return get_user_by_id(user_id)


jwt = JWT(authentication_handler=authenticate_user,
          identity_handler=identify_user)


# TODO: Refactor to remove code duplication, add caching


def get_user(username):
    return models.User.get(username=username)


def get_user_by_id(userId):
    return models.User.get(id=userId)


def get_permissions_by_username(username):
    permissions = get_user(username).permissions
    if permissions is not None:
        permissions = permissions.__dict__
        permissions.pop('_sa_instance_state')
        permissions.pop('id')

    return permissions


def set_permissions_by_username(username, permissions):
    ccaller_permissions = current_identity.permissions

    error = Forbidden('You do not have the permissions to do this.')

    if not ccaller_permissions.master:
        if not ccaller_permissions.admin:
            # If you're not a master or admin you can't touch this.
            raise error
        if permissions['admin']:
            # You MUST be a master to promote admins
            raise error

    permissionsObj = models.User.get_or_die(username=username).permissions

    if permissionsObj.master:
        # This user's permissions cannot be set through calls!
        raise error

    permissionsObj.update_permissions(permissions)
    util.try_merge(permissions=permissionsObj)


def create_user(email, username, password):
    # TODO: registration email
    permissions = models.UserPermissions()
    user = models.User(
        email=email,
        username=username,
        password=password,
        permissions=permissions
    )
    util.try_add(user=user, logger=logger)
    util.try_add(permissions=permissions, logger=logger)


def update_password(user, password):
    """
        params:
            user: A User object
            password: the users' new password
        return: boolean, whether the change was successful
    """
    user.change_password(password)
    util.try_merge(user=user, logger=logger)
