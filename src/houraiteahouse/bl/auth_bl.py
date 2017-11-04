from flask import request
from functools import wraps
from houraiteahouse.route import request_util
from houraiteahouse.storage import auth_storage, models
from werkzeug.exceptions import Unauthorized, Forbidden, InternalServerError, \
    NotFound


# Signin/signout calls
# TODO: Session caching for active sessions


def start_user_session(username, password, remember_me):
    """
    Verifies the user has provided the correct password and initiates a new session
    :param username: Username attempting login
    :type username: basestring
    :param password: User-provided password to validate for authN
    :type password: basestring
    :param remember_me: Whether to initiate a long-lasting session
    :type remember_me: Boolean
    :return: Either a new user session
    :rtype: houraiteahouse.storage.models.UserSession
    """
    error = Unauthorized('Invalid username or password.')
    if username is None or password is None:
        raise error
    if remember_me is None:
        remember_me = False
    try:
        user = models.User.get_or_die(username=username)
    except NotFound:
        raise error from None
    if authenticate_user(user, password):
        userSession = auth_storage.new_user_session(user, remember_me)
        ret = {
            'username': userSession.user.username,
            'email': userSession.user.email,
            'session_id': userSession.get_uuid(),
            'permissions':  userSession.get_user().permissions.__dict__
        }
        ret['permissions'].pop('_sa_instance_state')
        if not remember_me:
            ret['expiration'] = userSession.expiration
        return ret
    raise error


def get_user_for_session(session_id):
    """
    Fetches the user data associated with the given session ID
    :param session_id: Session ID associated with the desired user
    :type session_id: basestring
    :return: User object associated with the given session
    :rtype: houraiteahouse.storage.models.User
    """
    userSession = auth_storage.get_user_session(session_id)
    if userSession is None or not userSession.is_valid():
        raise Unauthorized('User is not logged in!')
    return userSession.get_user()


def close_user_session(session_id):
    """
    Closes the session associated with the given session ID
    :param session_id: The session ID to close
    :type session_id: basestring
    """
    auth_storage.close_user_session(session_id)


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
            'Failed to update password.  Please try again later.')


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


def authentication_check(session_id):
    """
    Validates that the given session is valid and returns session data if it is
    :param session_id: The session ID to check for validity
    :type session_id: basestring
    :return: Blob containing session status and, if relevant, permissions & expiration
    :rtype: dict
    """
    if session_id is None:
        return {'status': False}
    userSession = auth_storage.get_user_session(session_id)
    if not(userSession and userSession.is_valid):
        return {'status': False}
    ret = {
        'status': True,
        'permissions': userSession.user.permissions.__dict__,
        'expiration': userSession.expiration
    }
    ret['permissions'].pop('_sa_instance_state')
    return ret


def authenticate(func):
    """
    AuthN decorator.  Applying this decorator to a method will require any request to
    successfully pass an authentication challenge or return an error response.
    :param func: Method to decorate
    :type func: callable
    :return: Wrapped method
    :rtype: callable
    """
    @wraps(func)
    def authenticate_and_call(*args, **kwargs):
        """
        Checks if the request passes an authN challenge and invokes func on success
        :param args: Arguments to give to func
        :type args: list
        :param kwargs: Keyword arguments to give to func
        :type kwargs: dict
        :return: Results of func call if authN challenge passes
        """
        flag = False
        # reqdat = request.data or request.args
        can_auth = request.json and 'session_id' in request.json
        if can_auth:
            flag = authentication_check(
                request.json['session_id'])['status']
        if not flag:
            raise Unauthorized('You must be logged in to perform this action.')
        return func(*args, **kwargs)
    return authenticate_and_call


def authorization_check(action_type, session_id):
    """
    Authorization check.  Validates that the permissions for the given session include
    the requested action type.
    :param action_type: The permission type to validate
    :type action_type: basestring
    :param session_id: The ID of the session attempting to perform the requested action
    :type session_id: basestring
    :return: Result of (implicit) authN and (explicit) authZ check
    :rtype: Boolean
    """
    if session_id is None or action_type is None:
        return False
    userSession = auth_storage.get_user_session(session_id)
    if userSession is None or not userSession.is_valid:
        return False
    permissions = userSession.user.permissions.__dict__
    # 'master' implies server & db access and thus always has permission
    return permissions['master'] or permissions[action_type]


# Decorator to require authorization for requests
def authorize(action_type):
    """
    AuthZ decorator.  Applying this decorator to a method will require any calls to it
    pass an authorization check for the specified action type.
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
        @authenticate
        def authorize_and_call(*args, **kwargs):
            """
            Checks if the request passes an authZ challenge and invokes func on success
            :param args: Arguments to give to func
            :type args: list
            :param kwargs: Keyword arguments to give to func
            :type kwargs: dict
            :return: Results of func call if authN challenge passes
            """
            reqdat = request.json or request.args
            # The authenticate decorator has already guaranteed the request
            # data is present
            if not authorization_check(action_type, reqdat['session_id']):
                raise Forbidden('You do not have permission to do this.')
            return func(*args, **kwargs)
        return authorize_and_call

    return authz_wrapper
