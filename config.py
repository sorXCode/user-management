import os
from datetime import timedelta

basedir = os.path.abspath(os.path.dirname(__file__))

class Production:
    SECRET_KEY = os.environ.get("SECRET_KEY")
    DEBUG = bool(os.environ.get("DEBUG", False))
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'production_db.sqlite')

class Development:
    SECRET_KEY = os.environ.get("SECRET_KEY")
    DEBUG = True
    PERMANENT_SESSION_LIFETIME = timedelta(days=1)
    SESSION_REFRESH_EACH_REQUEST = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'development_db.sqlite')


class Test:
    SECRET_KEY = os.environ.get("SECRET_KEY")
    TESTING = True
    WTF_CSRF_ENABLED = False
    SERVER_NAME = '127.0.0.1:5000'
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'test_db.sqlite')


config = {
    'development': Development,
    'test': Test,
    'default': Development
}