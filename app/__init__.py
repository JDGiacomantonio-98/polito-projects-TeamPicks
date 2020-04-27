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
from manager import db_exist
from config import set_Config

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
@click.argument('config_key', default='pm')
@with_appcontext
def db_build(config_key):
    if config_key == 'pm':
        current_app.config.from_object(set_Config(pm=True))
    elif config_key == 'env':
        current_app.config.from_object(set_Config())
    # here add an --all argument whose create all db files and models
    if not db_exist(current_app):
        print("\nSUCCESS : application ready to run.")
    else:
        print("\nWARNING : detected an already existing db file for this configuration profile.\n")
    db.create_all()


@click.command(name='reset', help='Drops all table in db file used by specified config.')
@click.argument('config_key', default='pm')
@with_appcontext
def db_reset(config_key):
    if config_key == 'pm':
        current_app.config.from_object(set_Config(pm=True))
    elif config_key == 'env':
        current_app.config.from_object(set_Config())
    # here add an --all argument whose create all db files and models
    if current_app.config['ENV'] == 'production':
        c = str(input('\nThe data you are trying to erase belongs to a PRODUCTION environment!\n'
                      'If you confirm this action all sensible information stored in the actual database will be lost forever.\n\n'
                      'Press [D] to confirm this action : '))
        if c.lower() != 'd':
            print('INFO : no action has been taken.')
            exit(0)
        db.drop_all()
        print("\nSUCCESS : all data have been dropped.")
        # ask if to remove the db file
    else:
        if db_exist(current_app):
            db.drop_all()
            print("\nSUCCESS : all data have been dropped.")
            # ask if to remove the db file
        else:
            print("\nWARNING : any db file has been detected for this configuration profile.\n"
                  "\t  The command ended with no action.")


def create_app():
    app = Flask(__name__)
    try:
        app.config.from_object(set_Config())
        if app.config['SECRET_KEY']:
            print("\n===========================\n"
                  "RUNNING CONFIG: {}\n{}\n".format(app.config['ENV'], app.config))
        else:
            print('\nThe application factory has been closed.')
            return None
    except:
        print('\nThe application factory has been closed.')
        return None
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

    from app.users import users
    app.register_blueprint(users)

    app.cli.add_command(db_build)
    app.cli.add_command(db_reset)

    return app
