import os
basedir = os.path.abspath(os.path.dirname(__file__))

class BaseConfig(object):
    SECRET_KEY = 'secretkey'
    DEBUG = True
    BCRYPT_LOG_ROUNDS = 13
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://houraiteahouse:H0r41T34Hou$3@localhost/houraiteahouse'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
