from teamgate import app, db
from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager

db_migration = Migrate(app, db)
manager = Manager(app)
# creates a terminal command called db whose inherit all MigrateCommand class methods
manager.add_command('db', MigrateCommand)   # $ python db_manage.py db

if __name__ == '__main__':
    manager.run()
