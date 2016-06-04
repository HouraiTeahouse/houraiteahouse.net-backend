import json
from flask import Flask, request, session
from houraiteahouse.app import app, bcrypt, db
from .user import User
from .. import request_util


@app.route('/auth/register', methods=['POST'])
def register():
    json_data = request.data
    print(json_data)
    user = User(
        email = json_data['email'],
        password = json_data['password'],
        username = json_data['username']
    )
    try:
        db.session.add(user)
        db.session.commit()
        success = True
    except Exception as e:
        success = False
    db.session.close()
    if success:
        return request_util.generate_success_response('success', 'plain/text')
    return request_util.generate_error_response(400, 'A user with this name or email already exists.')


@app.route('/auth/login', methods=['POST'])
def login():
    json_data = request.data
    user = User.query.filter_by(username=json_data['username']).first()
    isValidUser = user is not None
    if isValidUser and bcrypt.check_password_hash(user.password, json_data['password']):
        session['logged_in'] = True
        session['username'] = user.username
        session['admin'] = user.admin
        # session['authNFailures'] = 0
        return request_util.generate_success_response(json.dumps({'result': True}), 'application/json')
    else:
        #if isValidUser:
        #    if session.get('authNFailures'):
        #        session['authNFailures'] = session.get('authNFailures') + 1
        #    else:
        #        session['authNFailures'] = 1
        #    if session['authNFailures'] > 5:
        #        user.lock_account()
        #        return request_util.generate_response(403, 'Login attempts exceeded. We have locked your account, check your email for instructions to unlock your account.')
        # Log nothing if the user does not exist - we can't exactly lock an invalid account
        # TODO: Do we want to limit login attempts for invalid usernames?
        return request_util.generate_error_response(401, 'Invalid Username or Password')


@app.route('/auth/logout', methods=['POST'])
def logout():
    session.pop('logged_in', None)
    session.pop('username', None)
    return request_util.generate_success_response('Logout Successful', 'plain/text')


@app.route('/auth/status', methods=['GET'])
def status():
    return request_util.generate_response(200, json.dumps({'status': session.get('logged_in') and session['logged_in']}), 'application/json')


@app.route('/auth/update', methods=['POST'])
def change_password():
    if session.get('logged_in') and session['logged_in']:
        json_data = request.data
        user = User.query.filter_by(username=session['username']).first()
        if bcrypt.check_password_hash(user.password, json_data['oldPassword']):
            try:
                user.password = bcrypt.generate_password_hash(json_data['newPassword'])
                db.session.merge(user)
                db.session.commit()
                return request_util.generate_success_response('Update successful', 'plain/text')
            except Exception as e:
                return request_util.generate_error_response(500, 'Failed to update password.')
        return request_util.generate_error_response(400, 'Current password is incorrect.')
    return request_util.generate_error_response(401, 'You must be logged in to perform this action.')
