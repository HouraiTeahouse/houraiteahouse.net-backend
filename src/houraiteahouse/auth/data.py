import logging

from datetime import datetime
from houraiteahouse.app import app, db
from houraiteahouse import models

logger = logging.getLogger(__name__)


def new_user_session(user, remember_me):
    userSession = models.UserSession(user, remember_me)
    uuid = userSession.get_uuid()
    # Allow errors to propogate up the stack
    db.session.add(userSession)
    db.session.commit()
    db.session.expunge(userSession)
    db.session.close()
    return get_user_session(uuid)


def get_user_session(session_uuid):
    return models.UserSession.query.filter_by(session_uuid=session_uuid).first()


def close_user_session(session_uuid):
    userSession = models.UserSession.query.filter_by(session_uuid=session_uuid).first()
    if userSession is None:
        return
    userSession.valid_before = datetime.utcnow()
    db.session.merge(userSession)
    db.session.commit()
    db.session.close()


def get_user(username):
    return models.User.query.filter_by(username=username).first()
    

def get_user_by_id(userId):
    return models.User.query.filter_by(user_id=userId).first()


def get_permissions_by_username(username):
    permissions = models.User.query.filter_by(username=username).first().get_permissions()
    if permissions is not None:
        permissions = permissions.__dict__
        permissions.pop('_sa_instance_state')
        permissions.pop('permissions_id')
    
    return permissions


def set_permissions_by_username(username, permissions, session_uuid):
    callerPermissions = get_user_session(session_uuid).get_user().get_permissions()
    
    if not callerPermissions.master:
        if not callerPermissions.admin:
            # If you're not a master or admin you can't touch this.
            return False
        if permissions['admin']:
            # You MUST be a master to promote admins
            return False
            
    permissionsObj = models.User.query.filter_by(username=username).first().get_permissions()
    
    print(permissions)

    if permissionsObj.master:
        # This user's permissions cannot be set through calls!
        return False

    try:
        permissionsObj.update_permissions(permissions)
    except:
        return False
    
    db.session.merge(permissionsObj)
    db.session.commit()
    db.session.close()
    return True


def create_user(email, username, password):
    # TODO: registration email
    permissions = models.UserPermissions()
    user = models.User(
        email = email,
        username = username,
        password = password,
        permissions = permissions
    )
    try:
        db.session.add(user)
        db.session.add(permissions)
        db.session.commit()
        success = True
    except Exception as e:
        success = False
    db.session.close()
    return success


def update_password(user, password):
    user.change_password(password)
    try:
        db.session.add(user)
        db.session.commit()
        success = True
    except Exception as e:
        success = False
    db.session.close()
    return success