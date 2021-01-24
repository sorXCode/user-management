from unittest import TestCase
from faker import Faker 
from app import app, db
from config import config
from user.models import User, Role

fake = Faker()
class BaseTestCase(TestCase):
    user_data = {
            "email": fake.email(),
            "password": fake.text()
        }

    def setUp(self):
        super().setUp()

        app.config.from_object(config['test'])
        self.app_context = app.app_context()
        self.app_context.push()
        
        self.test_client = app.test_client()

        # setup default db, roles, users

        # Dropping and creating tables on signup test\
        # to ensure retest success
        db.drop_all()
        db.create_all()
        Role.insert_roles()
        # create default user for tests
        super_admin = {"email": self.user_data["email"]}
        super_admin = User(**super_admin)
        super_admin.password = self.user_data["password"]
        super_admin.role = Role.query.filter_by(name="super_admin").first()
        db.session.commit()
        
        
    def tearDown(self):
        super().tearDown()
        self.app_context.pop()

