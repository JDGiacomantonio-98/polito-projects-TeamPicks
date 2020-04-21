#   runs the Flask application instance created by __init__.py

from app import create_app
from manager import db_exist

if __name__ == '__main__':
    app = create_app()
    if db_exist(app):
        app.run()
    else:
        print('\nERROR: No active db file has been detected in the current working directory.\n'
              'Please run < flask build > command to setup a new db file.')
