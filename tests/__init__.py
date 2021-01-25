from unittest import TestCase
from faker import Faker
from app import app, db
from config import config
from user.models import User, Role

fake = Faker()


class BaseTestCase(TestCase):
    user_data = {
        "super_admin":
            {"email": fake.email(),
             "password": fake.text()},
        "admin":
            {"email": fake.email(),
             "password": fake.text()},
        "user":
            {"email": fake.email(),
             "password": fake.text()},
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
