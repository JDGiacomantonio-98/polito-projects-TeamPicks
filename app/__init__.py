#    FLASK APP INIT MODULE -- First executed module
#    Initialize all needed objects to make app run properly

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail
from app.config import Config
from config import config


db = SQLAlchemy()
pswBurner = Bcrypt()

loginManager = LoginManager()
loginManager.session_protection = 'strong'
loginManager.login_view = 'users.login'
loginManager.login_message_category = 'info'

mail = Mail()


def create_app(CONFIG_KEY):
    from app.main.routes import main
    from app.errors.handlers import errors
    from app.users_glb.routes import users

    app = Flask(__name__)
    app.config.from_object(config[CONFIG_KEY])

    db.init_app(app)
    pswBurner.init_app(app)
    loginManager.init_app(app)
    mail.init_app(app)

    app.register_blueprint(main)
    app.register_blueprint(errors)
    app.register_blueprint(users)

    return app
