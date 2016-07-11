from flask import request, session
from houraiteahouse.app import app, bcrypt, db
from . import data

# Signin/signout calls

def start_user_session(username, password, remember_me):
    user = data.get_user(username)
    if authenticate_user(user, password):
        userSession = data.new_user_session(user, remember_me)
        ret = dict()
        ret['sessionId'] = userSession.get_uuid()
        ret['permissions'] = userSession.get_user().permissions.__dict__
        ret['permissions'].pop('_sa_instance_state')
        return ret
    return None


def get_user_for_session(session_id):
    userSession = data.get_user_session(session_id)
    if userSession is None or not userSession.is_valid():
        raise Exception('User is not logged in!')
    return userSession.get_user()


def close_user_session(session_id):
    data.close_user_session(session_id)


def change_password(username, old_password, new_password):
    user = data.get_user(username)
    if not authenticate_user(user, old_password):
        return False
    if data.update_password(user, new_password):
        return True
    raise Exception('Failed to update password.  Please try again later.')
    
    
# Primary authN logic

def authenticate_user(user, password):
    return user is not None and password is not None and user.check_password(password)


def authentication_check(session_id):
    if session_id is None:
        return False
    userSession = data.get_user_session(session_id)
    return userSession is not None and userSession.is_valid()


# Decorator to require authentication for functions
def authenticate(func):
    def authenticate_and_call(*args, **kwargs):
        if request is None or request.data is None or not 'session_id' in request.data or not authentication_check(request.data['session_id']):
            raise Exception('You must be logged in to perform this action!')
        return func(*args, **kwargs)
    return authenticate_and_call


# Primary authZ logic.  Includes authN check

def authorization_check(action_type, session_id):
    if session_id is None or action_type is None:
        return False
    userSession = get_user_session(session_id)
    if userSession is None or not userSession.is_valid():
        return False
    permissions = userSession.get_user().permissions
    return permissions[action_type]
    

# Decorator to require authorization for functions
def authorize(action_type):
    def wrapper(func):
        def authorize_and_call(*args, **kwargs):
            # The authenticate decorator has already guaranteed the request data is present
            if request is None or request.data is None or not 'session_id' in request.data or not authorization_check(action_type, request.data['session_id']):
                raise Exception('You do not have permission to perform this action!')
            return func(*args, **kwargs)
        return authorize_and_call
    return wrapper
