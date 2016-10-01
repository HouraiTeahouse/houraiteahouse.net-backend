import os
basedir = os.path.abspath(os.path.dirname(__file__))

class BaseConfig(object):
    DEBUG = True
    BCRYPT_LOG_ROUNDS = 13
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    f = open('/var/htwebsite/secretkey', 'r')
    SECRET_KEY = f.readline()[:-1]
    f.close()

    f = open('/var/htwebsite/mysqlcreds', 'r') # This file must exist
    username = f.readline()[:-1]
    password = f.readline()[:-1]
    database = f.readline()[:-1]
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://{0}:{1}@127.0.0.1/{2}?charset=utf8&unix_socket=/run/mysqld/mysqld.sock'.format(username, password, database)
    f.close()
