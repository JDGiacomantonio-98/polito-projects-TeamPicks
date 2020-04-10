import os
from datetime import timedelta


class Config:
    # needed to protect application from modifying cookies and cross site forgery request attacks
    # generated randomly by secret.token_hex(20)
    SECRET_KEY = os.environ.get('TEAMGATE[__SECRETKEY__]')
        # associate a local sql-lite server to the application
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEAMGATE[__DATABASE_URI__]')
    MAIL_SERVER = 'smtp.googlemail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USE_SSL = False
    MAIL_USERNAME = os.environ.get('TEAMGATE[__@USER__]')
    MAIL_PASSWORD = os.environ.get('TEAMGATE[__@PSW__]')
    MAIL_DEFAULT_SENDER = os.environ.get('TEAMGATE[__@USER__]')
