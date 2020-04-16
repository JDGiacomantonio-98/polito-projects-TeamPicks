# runs the Flask application instance created by __init__.py
import os
from os import environ
from app import create_app

# here a menu can be added in order to create different instances of app working with different Configs
print('==================')
c = str(input('SELECT APP CONFIG\n==================\n'
              '[D]evelopment\n'
              '[T]esting\n'
              '[P]roduction\n\n'
              '[Q]uit factory\n'
              'press < Enter > to run Defaults :\t'
              )
        )
if c:
    c = c.lower()
    if c == 'd':
        os.environ['FLASK_ENV'] = 'development'
    elif c == 't':
        os.environ['FLASK_ENV'] = 'testing'
    elif c == 'p':
        os.environ['FLASK_ENV'] = 'production'
    else:
        exit(-1)
    app = create_app(c)
else:
    os.environ['FLASK_ENV'] = 'development'
    app = create_app()

if __name__ == '__main__':
    app.run()
