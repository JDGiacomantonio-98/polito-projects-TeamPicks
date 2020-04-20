import os
import datetime
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))


class Config(object):
    # needed to protect application from modifying cookies and cross site forgery request attacks
    # generated randomly by secret.token_hex(20)
    SECRET_KEY = os.environ.get('TEAMPICKS[__SECRETKEY__]')
    PERMANENT_SESSION_LIFETIME = datetime.timedelta(minutes=25)
    # associate a local sql-lite server to the application
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAIL_SERVER = 'smtp.googlemail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USE_SSL = False
    MAIL_USERNAME = os.environ.get('TEAMPICKS[__@USER__]')
    MAIL_PASSWORD = os.environ.get('TEAMPICKS[__@PSW__]')
    MAIL_DEFAULT_SENDER = os.environ.get('TEAMPICKS[__@USER__]')


class DevConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'DEV.db')


class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'TEST.db')


class ProdConfig(Config):
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEAMPICKS[__DATABASE_URI__]')


config = {
    'd': DevConfig,
    't': TestConfig,
    'p': ProdConfig,
    'def': DevConfig
}
