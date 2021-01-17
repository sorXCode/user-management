import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Production:
    SECRET_KEY = os.environ["SECRET_KEY"]
    DEBUG = bool(os.environ.get("DEBUG", False))
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'production_db.sqlite')

class Development:
    SECRET_KEY = os.environ["SECRET_KEY"]
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'development_db.sqlite')


class Test:
    SECRET_KEY = os.environ["SECRET_KEY"]
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'test_db.sqlite')



config = {
    'development': Development,
    'test': Test,
    'default': Development
}