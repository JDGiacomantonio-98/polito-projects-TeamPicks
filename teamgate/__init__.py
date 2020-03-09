"""
    FLASK APP INIT MODULE -- First executed module
    Initialize all needed objects to make app run properly
"""

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail

app = Flask(__name__)

""" needed to protect application from modifying cookies and cross site forgery request attacks """
app.config['SECRET_KEY'] = '2f2a6b20a230fda4e91252334f67d57725100c92' """ generated randomly by secret.token_hex(20) """

""" associate a local sql-lite server to the application """
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'

db = SQLAlchemy(app)
pswBurner = Bcrypt(app)

loginManager = LoginManager(app)
loginManager.login_view = 'login'

""" following instruction is located here in order to avoid circular imports when app.run """
from teamgate import routes
