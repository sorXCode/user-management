from . import BaseTestCase, db, fake
from flask import url_for
from flask_login import current_user
from .utils import login, logout, register


class TestAccountCreation(BaseTestCase):
    another_super_admin = {"email": fake.email(), "password": fake.text(), "user_type": "super-admin"}
    admin_one = {"email": fake.email(), "password": fake.text(), "user_type": "admin"}
    user_one = {"email": fake.email(), "password": fake.text(), "user_type": "user"}


    def test_anonymous_create_account(self):
        with self.test_client as test_client:
            # check that no user is logged in
            self.assertEqual(current_user, None)

            # register a user
            register(test_client, self.another_super_admin)
            # login with newly registered credentials
            login(test_client, self.another_super_admin)

            self.assertEqual(current_user.is_authenticated, False)
    
    def test_super_admin_create_super_admin(self):
        with self.test_client as test_client:
            # login super_admin account
            login(test_client, self.user_data)
            self.assertEqual(current_user.is_super_admin(), True)

            # create another super_admin
            register(test_client, self.another_super_admin)
            # logout and login newly created account
            logout(test_client)
            login(test_client, self.another_super_admin)

            self.assertEqual(self.another_super_admin["email"], current_user.email)
            self.assertEqual(current_user.is_super_admin(), True)
            logout(test_client)

    def test_super_admin_create_admin(self):
        with self.test_client as test_client:
            # login super_admin account
            login(test_client, self.user_data)
            self.assertEqual(current_user.is_super_admin(), True)

            # create admin
            register(test_client, self.admin_one)

            # logout and login newly created account
            logout(test_client)
            login(test_client, self.admin_one)

            self.assertEqual(self.admin_one["email"], current_user.email)
            self.assertEqual(current_user.is_admin(), True)
            logout(test_client)
    
    def test_super_admin_create_user(self):
        with self.test_client as test_client:
            # login super_admin account
            login(test_client, self.user_data)
            self.assertEqual(current_user.is_super_admin(), True)

            # create user
            response = register(test_client, self.user_one)
            self.assertIn(b"cannot create account", response.data)
            # logout
            logout(test_client)
            
    
            


