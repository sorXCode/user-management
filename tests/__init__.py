from unittest import TestCase

from app import app, db
from config import config


class BaseTestCase(TestCase):
    user_data = {
            "email": "root@root.com",
            "password": "root"
        }

    def setUp(self):
        super().setUp()

        app.config.from_object(config['test'])
        self.app_context = app.app_context()
        self.app_context.push()
        
        self.test_client = app.test_client()
        
    def tearDown(self):
        super().tearDown()
        self.app_context.pop()
