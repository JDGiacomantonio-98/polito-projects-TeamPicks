from os import path, getenv, environ
from datetime import timedelta
from dotenv import load_dotenv

basedir = path.abspath(path.dirname(__file__))
load_dotenv(path.join(basedir, '.env'))


class Config(object):
    # needed to protect application from modifying cookies and cross site forgery request attacks
    # generated randomly by secret.token_hex(20)
    SECRET_KEY = getenv('SECRET_KEY')
    PERMANENT_SESSION_LIFETIME = timedelta(minutes=20)
    # associate a local sqlite server to the application
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAIL_SERVER = getenv('MAIL_SERVER')
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USE_SSL = False
    MAIL_USERNAME = getenv('MAIL_USERNAME')
    MAIL_PASSWORD = getenv('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = getenv('MAIL_USERNAME')


class DevConfig(Config):
    DEBUG = True
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + path.join(basedir, 'DEV.db')


class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + path.join(basedir, 'TEST.db')


class ProdConfig(Config):
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = getenv('SQLALCHEMY_DATABASE_URI')


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
        ck = getenv('CONFIG')
    if ck == 'd' or ck == 'def':
        environ['FLASK_ENV'] = 'development'
    elif ck == 't':
        environ['FLASK_ENV'] = 'testing'
    elif ck == 'p':
        environ['FLASK_ENV'] = 'production'
    else:
        return None
    return config[ck]
