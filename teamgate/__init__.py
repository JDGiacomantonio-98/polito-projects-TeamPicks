#    FLASK APP INIT MODULE -- First executed module
#    Initialize all needed objects to make app run properly

import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail

app = Flask(__name__)

# needed to protect application from modifying cookies and cross site forgery request attacks
# generated randomly by secret.token_hex(20)
app.config['SECRET_KEY'] = os.environ.get('TEAMGATE[__SECRETKEY__]')
# associate a local sql-lite server to the application
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('TEAMGATE[__DATABASE_URI__]')
app.config['MAIL_SERVER'] = 'smtp.googlemail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
# The following Config constants need to be hided from plain code. This can be done setting them as env variables
app.config['MAIL_USERNAME'] = os.environ.get('TEAMGATE[__@USER__]')
app.config['MAIL_PASSWORD'] = os.environ.get('TEAMGATE[__@PSW__]')
app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('TEAMGATE[__@USER__]')

db = SQLAlchemy(app)
pswBurner = Bcrypt(app)

loginManager = LoginManager(app)
loginManager.session_protection = 'strong'
loginManager.login_view = 'login'
loginManager.login_message_category = 'info'

mail = Mail(app)

# following instruction is located here in order to avoid circular imports when app.run
from teamgate import routes
