import unittest
from os import path

from sqlalchemy.exc import IntegrityError, OperationalError

from devkit import create_userbase


class DBTester(unittest.TestCase):
    def __init__(self, app=None, db=None):
        super().__init__()
        self.app = app
        self.db = db

    def init_app(self, app, db):
        self.app = app
        self.db = db

    def test_db_ready(self):
        print('testing database ...')
        if self.test_db_exist():
            if self.test_db_connection():
                return True
        return False

    def test_db_exist(self):
        if 'sqlite:///' in self.app.config['SQLALCHEMY_DATABASE_URI']:
            db_uri = str(self.app.config['SQLALCHEMY_DATABASE_URI']).replace('sqlite:///', '')
        if path.exists(db_uri):
            return True
        print('(!) ERROR: No active db has been detected for the current working app.')
        return False

    def test_db_connection(self):
        if self.test_db_read():
            if self.test_db_write():
                print('CONNECTION ON : {}'.format(self.app.config['SQLALCHEMY_DATABASE_URI']))
                return True
        print('(!) ERROR : failed connection')
        print('(!) INFO  : have you run upgrade() from last migration file?')
        return False

    @staticmethod
    def test_db_read():
        from app.dbModels import User, Owner, Pub

        try:
            User.query.first()
            Owner.query.first()
            Pub.query.first()
        except OperationalError:
            return False
        return True

    def test_db_write(self):
        try:
            create_userbase(test_db=True)
        except IntegrityError:
            self.test_db_write()
        except RuntimeError:
            return False
        return True


if __name__ == '__main__':
    unittest.main()
