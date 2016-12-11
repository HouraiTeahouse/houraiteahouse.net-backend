import os
from .util.file_utils import load_json_file

basedir = os.path.abspath(os.path.dirname(__file__))


# Base configuration
class BaseConfig(object):
    BCRYPT_LOG_ROUNDS = 13
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = 'secret_key'
    SQLALCHEMY_DATABASE_URI = 'sqlite://'


# Config used for local development testing
# loads config information from a JSON file
class DevelopmentConfig(BaseConfig):

    def __init__(self, config_file=None):
        config = load_json_file(config_file or '/var/htwebsite/config.json')

        self.DEBUG = config['enableDebug']
        self.BCRYPT_LOG_ROUNDS = config['bcryptLogRounds']
        self.SQLALCHEMY_TRACK_MODIFICATIONS = config[
            'sqlalchemyTrackModifications']

        self.CACHE_TYPE = 'simple'
        self.CACHE_DEFAULT_TIMEOUT = 3600
        self.CACHE_THRESHOLD = 5000

        self.SECRET_KEY = config['secretKey']
        

        db_config = config['dbConfig']
        db_username = db_config['username']
        db_password = db_config['password']
        db_name = db_config['database']
        self.SQLALCHEMY_DATABASE_URI = \
            ('postgresql+psycopg2://{0}:{1}@127.0.0.1/{2}'
             '?client_encoding="utf-8"'
             ).format(db_username, db_password, db_name)


        self.REQUIRE_CONFIRMATION = config['email']['required']
        
        if(self.REQUIRE_CONFIRMATION):
            email_config = config['email']
            self.DOMAIN = email_config['domain'] # Used when generating URLs
            self.SECURITY_SALT = email_config['salt']
            self.MAIL_DEFAULT_SENDER = 'no-reply@houraiteahouse.net'
            self.MAIL_USE_TLS = False
            self.MAIL_USE_SSL = True
            self.MAIL_SERVER = email_config['server']
            self.MAIL_PORT = email_config['port']
            self.MAIL_USERNAME = email_config['username']
            self.MAIL_PASSWORD = email_config['password']


# Config used for unit testing
class TestConfig(BaseConfig):
    DEBUG = True
    TESTING = True
    REQUIRE_CONFIRMATION = False


# Config used for the production server
class ProductionConfig(DevelopmentConfig):

    def __init__(self, config_file=None):
        DevelopmentConfig.__init__(self, config_file)
