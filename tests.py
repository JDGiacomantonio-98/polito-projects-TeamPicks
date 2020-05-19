import unittest
from os import path
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
        try:
            create_userbase(test_db=True)
            print('CONNECTION ON : {}'.format(self.app.config['SQLALCHEMY_DATABASE_URI']))
            return True
        except:
            print('(!) ERROR : failed connection')
            return False


if __name__ == '__main__':
    unittest.main()
