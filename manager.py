import os
from sqlalchemy.exc import OperationalError


def select_Config():
    # Menu  to create different instances of app working with different Configs profiles
    print('==================')
    c = str(input('SELECT APP CONFIG\n'
                  '==================\n'
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
            exit(0)
    else:
        c = 'def'
        os.environ['FLASK_ENV'] = 'development'

    return c


#   i could think of creating an database unittest based on this func
def db_exist(app):
    if app.debug:
        if 'DEV.db' not in os.listdir('.'):
            return False
        else:
            return True
    elif app.testing:
        if 'TEST.db' not in os.listdir('.'):
            return False
        else:
            return True
    else:
        return True
