import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))


class Config(object):
    # needed to protect application from modifying cookies and cross site forgery request attacks
    # generated randomly by secret.token_hex(20)
    SECRET_KEY = os.environ.get('TEAMPICKS[__SECRETKEY__]')
        # associate a local sql-lite server to the application
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEAMPICKS[__DATABASE_URI__]')
    MAIL_SERVER = 'smtp.googlemail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USE_SSL = False
    MAIL_USERNAME = os.environ.get('TEAMPICKS[__@USER__]')
    MAIL_PASSWORD = os.environ.get('TEAMPICKS[__@PSW__]')
    MAIL_DEFAULT_SENDER = os.environ.get('TEAMPICKS[__@USER__]')


class DevConfig(Config):
    #DEBUG = True
    pass

class TestConfig(Config):
    #TESTING = True
    pass

class ProdConfig(Config):
    #DEBUG = False
    pass

config = {
    'd': DevConfig,
    't': TestConfig,
    'p': ProdConfig,
    'def': DevConfig
}
