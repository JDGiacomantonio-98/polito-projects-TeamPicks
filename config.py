import os
import datetime
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))


class Config(object):
    # needed to protect application from modifying cookies and cross site forgery request attacks
    # generated randomly by secret.token_hex(20)
    SECRET_KEY = os.getenv('SECRET_KEY')
    PERMANENT_SESSION_LIFETIME = datetime.timedelta(minutes=20)
    # associate a local sqlite server to the application
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAIL_SERVER = 'smtp.googlemail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USE_SSL = False
    MAIL_USERNAME = os.getenv('MAIL_USERNAME')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.getenv('MAIL_USERNAME')


class DevConfig(Config):
    DEBUG = True
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'DEV.db')


class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'TEST.db')


class ProdConfig(Config):
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.getenv('SQLALCHEMY_DATABASE_URI')


config = {
    'd': DevConfig,
    't': TestConfig,
    'p': ProdConfig,
    'def': DevConfig
}


def set_Config(pm=False):
    if pm:
        # print a menu to create different instances of app working with different Configs profiles
        print('==================')
        ck = str(input('SELECT APP CONFIG\n'
                      '==================\n'
                      '[D]evelopment\n'
                      '[T]esting\n'
                      '[P]roduction\n\n'
                      '[Q]uit factory\n'
                      'press < Enter > to run Defaults :\t'
                       )
                 ).lower()
        if ck == '':
            ck = 'def'
    else:
        ck = os.getenv('CONFIG')
    if ck == 'd' or ck == 'def':
        os.environ['FLASK_ENV'] = 'development'
    elif ck == 't':
        os.environ['FLASK_ENV'] = 'testing'
    elif ck == 'p':
        os.environ['FLASK_ENV'] = 'production'
    else:
        return None
    return config[ck]
