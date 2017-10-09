from flask import request
from flask_jwt import jwt_required
from functools import wraps
from houraiteahouse.route import request_util
from houraiteahouse.storage import auth_storage, models
from werkzeug.exceptions import Unauthorized, Forbidden, InternalServerError, \
    NotFound


# Signin/signout calls


def change_password(username, old_password, new_password):
    """
    Changes the password with the given user to the new password.
    The old password will be validated before any change is made.
    :param username: User who has requested password update
    :type username: basestring
    :param old_password: The provided old password to validate for authN
    :type old_password: basestring
    :param new_password: The provided new password to update to
    :type new_password: basestring
    """
    user = auth_storage.get_user(username)
    if not authenticate_user(user, old_password):
        raise Unauthorized()
    try:
        auth_storage.update_password(user, new_password)
    except:
        raise InternalServerError(
            'Failed to update password.  Please try again later.') from None


# Primary authN logic

def authenticate_user(user, password):
    """
    Validates that the given password is correct for the given user
    :param user: The User model object attempting authN
    :type user: houraiteahouse.storage.models.User
    :param password: The password being presented in the authN challenge
    :type password: basestring
    """
    return user and password and user.check_password(password)


def authentication_check():
    """
    Validates that the caller is a recognized identity
    :return: Blob containing session status and, if relevant, permissions &
      expiration
    :rtype: dict
    """
    if not current_identity:
        return {'status': False}
    ret = {
        'status': True,
        'permissions': current_identity.permissions.__dict__,
    }
    ret['permissions'].pop('_sa_instance_state')
    return ret

# Primary authZ logic.  Includes authN check

def authorization_check(action_type):
    """
    Authorization check.  Validates that the permissions for the current
      identity include the requested action type.
    :param action_type: The permission type to validate
    :type action_type: basestring
    :return: Result of (implicit) authN and (explicit) authZ check
    :rtype: Boolean
    """
    assert action_type is not None
    permissions = current_identity.permissions.__dict__
    # 'master' implies server & db access and thus always has permission
    return permissions['master'] or permissions[action_type]


# Decorator to require authorization for requests
def authorize(action_type):
    """
    AuthZ decorator.  Applying this decorator to a method will require any
      calls to it pass an authorization check for the specified action type.
      This includes an authN check.
    :param action_type: The permission type to validate
    :type action_type: basestring
    :return: Function wrapper
    :rtype: callable
    """
    def authz_wrapper(func):
        """
        Inner decorator logic.
        :param func: Method to wrap
        :type func: callable
        :return: Wrapped method
        :rtype: callable
        """
        @wraps(func)
        @jwt_required()
        def authorize_and_call(*args, **kwargs):
            """
            Checks if the request passes an authZ challenge and invokes func
              on success
            :param args: Arguments to give to func
            :type args: list
            :param kwargs: Keyword arguments to give to func
            :type kwargs: dict
            :return: Results of func call if authN challenge passes
            """
            reqdat = request.json or request.args
            # The authenticate decorator has already guaranteed the request
            # data is present
            if not authorization_check(action_type):
                raise Forbidden('You do not have permission to do this.')
            return func(*args, **kwargs)
        return authorize_and_call

    return authz_wrapper
