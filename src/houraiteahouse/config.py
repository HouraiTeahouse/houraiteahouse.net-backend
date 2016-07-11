import os
basedir = os.path.abspath(os.path.dirname(__file__))

class BaseConfig(object):
    DEBUG = True
    BCRYPT_LOG_ROUNDS = 13
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Fake for the sake of git commit.  This should be set manually on the host.
    SECRET_KEY = 'secretkey'
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://houraiteahouse:H0r41T34Hou$3@127.0.0.1/houraiteahouse?unix_socket=/run/mysqld/mysqld.sock'
