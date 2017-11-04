import logging

from datetime import datetime
from flask_sqlalchemy_cache import FromCache
from sqlalchemy import inspect, exc
from sqlalchemy.orm.session import Session
from houraiteahouse.storage import models
from houraiteahouse.storage import storage_util as util
from houraiteahouse.storage.models import db, cache
from werkzeug.exceptions import Forbidden

logger = logging.getLogger(__name__)


# TODO: Refactor to remove code duplication, add caching


def new_user_session(user, remember_me):
    """
    Opens a new session for the given user.
    :param user: User model the session has been requested for
    :type user: models.UserSession
    :param remember_me: Whether to make this a long-lasting session
    :type remember_me: Boolean
    :return: The new session
    :rtype: models.UserSession
    """
    user_session = models.UserSession(user, remember_me)
    uuid = user_session.session_uuid
    util.try_add(session=user_session, logger=logger)
    return get_user_session(uuid)


def get_user_session(session_uuid):
    """
    Fetches the session associated with the given session ID
    :param session_uuid: The session ID to query
    :type session_uuid: basestring
    :return: Session object associated with the ID if present
    :rtype: models.UserSession
    """
    return models.UserSession.query \
        .filter_by(session_uuid=session_uuid) \
        .options(FromCache(cache)) \
        .first()


def close_all_sessions(user_id):
    """
    Closes all sessions associated with a given user
    :param user_id: ID of the user to close all sessions for
    :type user_id: int
    """
    models.UserSession.query \
        .filter_by(user_id=user_id) \
        .options(FromCache(cache)) \
        .delete()
    db.session.commit()


def close_user_session(session_uuid):
    """
    Closes the session associated with the given session ID
    :param session_uuid: Session ID to close
    :type session_uuid: basestring
    """
    userSession = models.UserSession.query \
        .filter_by(session_uuid=session_uuid) \
        .options(FromCache(cache)) \
        .first()
    db.session.delete(userSession)
    db.session.commit()


def get_user(username):
    """
    Fetches the User model identified by the given username
    :param username: Username to query for
    :type username: basestring
    """
    return models.User.get(username=username)


def get_user_by_id(user_id):
    """
    Fetches the User model with the given ID
    :param user_id: User ID to query for
    :type user_id: int
    """
    return models.User.get(id=user_id)


def get_permissions_by_username(username):
    """
    Fetches the permissions model associated with the given username
    :param username: Username to query permissions for
    :type username: basestring
    :return: Permissions object associated with the given user
    :rtype: models.UserPermissions
    """
    permissions = get_user(username).permissions
    if permissions is not None:
        permissions = permissions.__dict__
        permissions.pop('_sa_instance_state')
        permissions.pop('id')

    return permissions


def set_permissions_by_username(username, permissions, session_uuid):
    """
    Attempts to update the given permissions associated with the given username to the provided new permissions.
    :param username: User whose permissions will be updated
    :type username: basestring
    :param permissions: New permissions to set
    :type permissions: dict
    :param session_uuid: Session ID of the caller.  Used as part of authZ check.
    :type session_uuid: basestring
    :return: Whether the permissions were updated successfully
    :rtype: Boolean
    """
    callerPermissions = get_user_session(session_uuid).user.permissions

    error = Forbidden('You do not have the permissions to do this.')

    if not callerPermissions.master:
        if not callerPermissions.admin:
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
    """
    Creates a new user with the given email address, username, and password
    :param email: User's email address
    :type email: basestring
    :param username: User's username
    :type username: basestring
    :param password: User's password
    :type password: basestring
    :return: Whether the creation was successful
    :rtype: Boolean
    """
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
    Updates a user's password
    :param user: User object to update password on
    :type user: models.User
    :param password: New password to set
    :type password: basestring
    :return: Whether the change was successful
    :rtype: Boolean
    """
    user.change_password(password)
    # Changing passwords should the user out of all of their sessions
    close_all_sessions(user.user_id)
    util.try_merge(user=user, logger=logger)
