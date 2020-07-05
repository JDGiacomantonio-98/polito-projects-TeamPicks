#    FLASK APP INIT MODULE -- First executed module
#    Initialize all needed objects to make app run properly

import click

from flask import Flask, current_app
from flask.cli import with_appcontext
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail
from flask_moment import Moment

from config import set_config
from tests import DBTester

db = SQLAlchemy()
migration = Migrate()
pswBurner = Bcrypt()

login_handler = LoginManager()
login_handler.session_protection = 'strong'
login_handler.login_view = 'users.login'
login_handler.login_message_category = 'info'

mail = Mail()
clock = Moment()
unittest = DBTester()


@click.command(name='build', help='Create a db file based on config specification.')
@click.argument('config_key', default='sel')
@with_appcontext
def db_build(config_key):
	if config_key == 'sel':
		current_app.config.from_object(set_config(select=True))
	elif config_key == 'env':
		current_app.config.from_object(set_config())
	else:
		quit()
	db.create_all()


@click.command(name='reset', help='Drops all table in db file used by specified config.')
@click.argument('config_key', default='sel')
@with_appcontext
def db_reset(config_key):
	if config_key == 'sel':
		current_app.config.from_object(set_config(select=True))
	elif config_key == 'env':
		current_app.config.from_object(set_config())
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


def create_app(config=None, db_only=False):
	app = Flask(__name__)
	try:
		app.config.from_object(config)
		print(f"RUNNING CONFIG: {app.config['ENV']}")
	except:
		print('\nThe application factory has been closed.')
		return None
	db.init_app(app)
	with app.app_context():
		print('running tests ...')
		unittest.init_app(app, db)
		if unittest.test_db_ready():
			if db_only:
				return app
			pswBurner.init_app(app)
			login_handler.init_app(app)
			mail.init_app(app)
			clock.init_app(app)
		else:
			print('(!) WARNING : some tests have failed while initiation the app. Please check your db connection again.')
			print('The following cli commands are available to cope with this issue:\n'
				  '* flask reset\n'
				  '* flask build\n')
		migration.init_app(app, db)

		from app.errors import errors
		app.register_blueprint(errors)

		from app.main import main
		app.register_blueprint(main)

		from app.users import users
		app.register_blueprint(users)

		app.cli.add_command(db_build)
		app.cli.add_command(db_reset)

	return app
