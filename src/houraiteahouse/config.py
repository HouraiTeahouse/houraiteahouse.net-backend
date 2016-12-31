import os
from .util.file_utils import load_json_file

basedir = os.path.abspath(os.path.dirname(__file__))


class BaseConfig(object):
    config = load_json_file('/var/htwebsite/config.json')

    DEBUG = config['enableDebug']
    BCRYPT_LOG_ROUNDS = config['bcryptLogRounds']
    SQLALCHEMY_TRACK_MODIFICATIONS = config['sqlalchemyTrackModifications']

    CACHE_TYPE = 'simple'

    SECRET_KEY = config['secretKey']

    db_config = config['dbConfig']
    db_username = db_config['username']
    db_password = db_config['password']
    db_name = db_config['database']
    SQLALCHEMY_DATABASE_URI = \
        'mysql+pymysql://{0}:{1}@127.0.0.1/{2}?charset=utf8&' \
        'unix_socket=/run/mysqld/mysqld.sock'.format(
            db_username, db_password, db_name)
