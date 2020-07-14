from os import path, getenv
from datetime import timedelta

from dotenv import load_dotenv

from devkit import config_menu, set_env


basedir = path.abspath(path.dirname(__file__))
load_dotenv(path.join(basedir, '.env'))


class Config(object):
	FLASKY_ADMIN = getenv('FLASKY_ADMIN')
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
	USERS_UPLOADS_BIN = getenv('USERS_UPLOADS_BIN')
	PUBS_UPLOADS_BIN = getenv('PUBS_UPLOADS_BIN')


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
	'development': DevConfig,
	'testing': TestConfig,
	'production': ProdConfig
}


def set_config(select=False):
	if select:
		return config[set_env(config_menu())]
	return config[set_env(selKey='d')]
