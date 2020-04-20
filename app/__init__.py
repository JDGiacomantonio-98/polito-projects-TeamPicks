#    FLASK APP INIT MODULE -- First executed module
#    Initialize all needed objects to make app run properly

import click
from flask import Flask,current_app
from flask.cli import with_appcontext
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail
from flask_moment import Moment
from config import config
from manager import db_exist


db = SQLAlchemy()
migration = Migrate()
pswBurner = Bcrypt()

login_handler = LoginManager()
login_handler.session_protection = 'strong'
login_handler.login_view = 'users.login'
login_handler.login_message_category = 'info'

mail = Mail()
clock = Moment()


@click.command(name='build', help='Create a db file based on config specification.')
@click.argument('config_key', default='def')
@with_appcontext
def db_build(config_key):
    config_key = str(config_key).lower()
    current_app.config.from_object(config[config_key])
    if not db_exist(current_app):
        print("\nSUCCESS : application ready to run.")
        if config_key == 'def':
            print("\t  Default option used : DEVELOPMENT\n")
    else:
        print("\nWARNING : detected an already existing db file for this configuration profile.\n")
    db.create_all()


@click.command(name='reset', help='Drops all table in db file used by specified config.')
@click.argument('config_key', default='def')
@with_appcontext
def db_reset(config_key):
    config_key = str(config_key).lower()
    if config_key == 'p':
        c = str(input('The data you are trying to erase belongs to a PRODUCTION environment!\n'
                      'If you confirm this action all sensible information stored in the actual database will be lost forever.\n\n'
                      'Press [D] to confirm this action : '))
        if c.lower() != 'd':
            pass
        current_app.config.from_object(config[config_key])
        db.drop_all()
        print("\nSUCCESS : all data have been dropped.")
    else:
        current_app.config.from_object(config[config_key])
        if db_exist(current_app):
            db.drop_all()
            print("\nSUCCESS : all data have been dropped.")
        else:
            print("\nWARNING : any db file has been detected for this configuration profile.\n"
                  "\t  The command ended with no action.")


def create_app(CONFIG_KEY='def'):
    if CONFIG_KEY != 's':
        app = Flask(__name__)

        app.config.from_object(config[CONFIG_KEY])

        if CONFIG_KEY == ('d' or 'def'):
            print(app.config)

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

        app.cli.add_command(db_build)
        app.cli.add_command(db_reset)

        return app
    else:
        pass
