import os
import logging
from .util.file_utils import load_json_file


basedir = os.path.abspath(os.path.dirname(__file__))


# Base configuration
class BaseConfig(object):
    BCRYPT_LOG_ROUNDS = 13
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = 'secret_key'
    SQLALCHEMY_DATABASE_URI = 'sqlite://'
    CACHE_TYPE = 'simple'


# Config used for local development testing
# loads config information from a JSON file
class DevelopmentConfig(BaseConfig):

    def __init__(self, config_file=None):
        config = load_json_file(config_file or '/var/htwebsite/config.json')

        self.DEBUG = config['enableDebug']
        self.BCRYPT_LOG_ROUNDS = config['bcryptLogRounds']
        self.SQLALCHEMY_TRACK_MODIFICATIONS = config[
            'sqlalchemyTrackModifications']

        self.SECRET_KEY = config['secretKey']

        db_config = config['dbConfig']
        db_username = db_config['username']
        db_password = db_config['password']
        db_name = db_config['database']
        self.SQLALCHEMY_DATABASE_URI = \
            ('postgresql+psycopg2://{0}:{1}@127.0.0.1/{2}'
             '?client_encoding="utf-8"'
             ).format(db_username, db_password, db_name)


# Config used for unit testing
class TestConfig(BaseConfig):
    DEBUG = True
    TESTING = True
    PRESERVE_CONTEXT_ON_EXCEPTION = False


# Config used for the production server
class ProductionConfig(DevelopmentConfig):

    def __init__(self, config_file=None):
        DevelopmentConfig.__init__(self, config_file)
