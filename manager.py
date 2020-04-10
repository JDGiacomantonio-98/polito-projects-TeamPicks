from app import db
from flask import current_app
from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager

migration = Migrate(current_app, db)
manager = Manager(current_app)

# creates a terminal command called db whose inherit all MigrateCommand class methods
# allow triggering migrations via terminal
manager.add_command('db', MigrateCommand)   # $ python db_manage.py db

if __name__ == '__main__':
    manager.run()
