import logging

from datetime import datetime
from flask_sqlalchemy_cache import FromCache
from sqlalchemy import inspect
from sqlalchemy.orm.session import Session
from houraiteahouse.storage import models
from houraiteahouse.storage import storage_util as util
from houraiteahouse.storage.models import db, cache

logger = logging.getLogger(__name__)


# TODO: Refactor to remove code duplication, add caching


def new_user_session(user, remember_me):
    user_session = models.UserSession(user, remember_me)
    uuid = user_session.session_uuid
    util.try_add(session=user_session, logger=logger)
    return get_user_session(uuid)


def get_user_session(session_uuid):
    return models.UserSession.get(session_uuid=session_uuid)


def close_user_session(session_uuid):
    user_session = get_user_session(session_uuid)
    if not user_session:
        return
    user_session.valid_before = datetime.utcnow()
    db.session.merge(user_session)
    db.session.commit()


def get_user(username):
    return models.User.get(username=username)


def get_user_by_id(userId):
    return models.User.get(id=userId)


def get_permissions_by_username(username):
    user = get_user(username).permissions
    if permissions is not None:
        permissions = permissions.__dict__
        permissions.pop('_sa_instance_state')
        permissions.pop('permissions_id')

    return permissions


def set_permissions_by_username(username, permissions, session_uuid):
    callerPermissions = get_user_session(session_uuid).user.permissions

    error = Forbidden('You do not have the permissions to do this.')

    if not callerPermissions.master:
        if not callerPermissions.admin:
            # If you're not a master or admin you can't touch this.
            raise error
        if permissions['admin']:
            # You MUST be a master to promote admins
            raise error

    permissionsObj = get_permissions_by_username(username)

    if permissionsObj.master:
        # This user's permissions cannot be set through calls!
        raise error

    permissionsObj.update_permissions(permissions)
    util.try_merge(permissionsObj)


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
    user.change_password(password)
    util.try_merge(user=user, logger=logger)
