#    FLASK APP INIT MODULE -- First executed module
#    Initialize all needed objects to make app run properly

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail
from flask_moment import Moment
from config import config


db = SQLAlchemy()
migration = Migrate()
pswBurner = Bcrypt()

login_handler = LoginManager()
login_handler.session_protection = 'strong'
login_handler.login_view = 'users.login'
login_handler.login_message_category = 'info'

mail = Mail()
clock = Moment()


def create_app(CONFIG_KEY='def'):
    app = Flask(__name__)
    app.config.from_object(config[CONFIG_KEY])

    db.init_app(app)
    migration.init_app(app, db)
    pswBurner.init_app(app)
    login_handler.init_app(app)
    mail.init_app(app)
    clock.init_app(app)

    from app.main import main
    app.register_blueprint(main)

    from app.errors import errors
    app.register_blueprint(errors)

    from app.users_glb import users
    app.register_blueprint(users)

    return app
