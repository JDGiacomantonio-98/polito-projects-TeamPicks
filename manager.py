from os import listdir
# from sqlalchemy.exc import OperationalError


#   a database unittest can be created based on this func
def db_exist(app):
    if app.debug:
        if 'DEV.db' not in listdir('.'):
            return False
        else:
            print('INFO : db file (development) detected!')
            print('CONNECTION ON : {}'.format(app.config['SQLALCHEMY_DATABASE_URI']))
            return True
    elif app.testing:
        if 'TEST.db' not in listdir('.'):
            return False
        else:
            print('INFO : db file (testing) detected!')
            print('CONNECTION ON : {}'.format(app.config['SQLALCHEMY_DATABASE_URI']))
            return True
    else:
        return True
