from flask import request
from functools import wraps
from houraiteahouse.route import request_util
from houraiteahouse.storage import auth_storage, models
from werkzeug.exceptions import Unauthorized, Forbidden, InternalServerError, \
                                NotFound


# Signin/signout calls
# TODO: Session caching for active sessions


def start_user_session(username, password, remember_me):
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
    userSession = auth_storage.get_user_session(session_id)
    if userSession is None or not userSession.is_valid():
        raise Unauthorized('User is not logged in!')
    return userSession.get_user()


def close_user_session(session_id):
    auth_storage.close_user_session(session_id)


def change_password(username, old_password, new_password):
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
    return user and password and user.check_password(password)


def authentication_check(session_id):
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

# Decorator to require authentication for requests
def authenticate(func):
    @wraps(func)
    def authenticate_and_call(*args, **kwargs):
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


# Primary authZ logic.  Includes authN check

def authorization_check(action_type, session_id):
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
    def authz_wrapper(func):
        @wraps(func)
        @authenticate
        def authorize_and_call(*args, **kwargs):
            reqdat = request.json or request.args
            # The authenticate decorator has already guaranteed the request
            # data is present
            if not authorization_check(action_type, reqdat['session_id']):
                raise Forbidden('You do not have permission to do this.')
            return func(*args, **kwargs)
        return authorize_and_call

    return authz_wrapper
