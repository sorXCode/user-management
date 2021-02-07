from . import BaseTestCase, db, fake
from flask import url_for
from flask_login import current_user
from .utils import login, logout, register
from .accounts import *

class TestAccountCreation(BaseTestCase):
    def test_anonymous_create_account(self):
        with self.test_client as test_client:
            # check that no user is logged in
            self.assertEqual(current_user, None)

            # register a user
            register(test_client, super_admin_2)
            # login with newly registered credentials
            login(test_client, super_admin_2)

            self.assertEqual(current_user.is_authenticated, False)

    def test_super_admin_create_super_admin(self):
        with self.test_client as test_client:
            create_account(self=self, test_client=test_client, user_data=self.user_data["super_admin"],
                           user_role="super_admin", new_account_data=super_admin_2, new_account_role="super_admin")

    def test_super_admin_create_admin(self):
        with self.test_client as test_client:
            create_account(self=self, test_client=test_client, user_data=self.user_data["super_admin"],
                           user_role="super_admin", new_account_data=admin_one, new_account_role="admin")

    def test_super_admin_create_user(self):
        with self.test_client as test_client:
            create_account(self=self, test_client=test_client, user_data=self.user_data["super_admin"],
                           user_role="super_admin", new_account_data=user_one, new_account_role="user",
                           should_be_successful=False)

    def test_admin_create_super_admin(self):
        admin = {"email": fake.email(
        ), "password": fake.text(), "user_type": "super-admin"}

        with self.test_client as test_client:
            create_account(self=self, test_client=test_client, user_data=self.user_data["admin"],
                           user_role="admin", new_account_data=admin, new_account_role="super_admin",
                           should_be_successful=False)

    def test_admin_create_admin(self):
        admin = {"email": fake.email(
        ), "password": fake.text(), "user_type": "admin"}

        with self.test_client as test_client:
            create_account(self=self, test_client=test_client, user_data=self.user_data["admin"],
                           user_role="admin", new_account_data=admin, new_account_role="admin")


    def test_admin_create_user(self):
        user = {**self.user_data["user"], "user_type": "user"}
        with self.test_client as test_client:
            create_account(self=self, test_client=test_client, user_data=self.user_data["admin"],
                           user_role="admin", new_account_data=user, new_account_role="user")


def create_account(self, test_client, user_data, user_role, new_account_data, new_account_role, should_be_successful=True):
    login(test_client, user_data)
    self.assertEqual(eval(f"current_user.is_{user_role}"), True)

    # create new_user
    response = register(test_client, new_account_data)

    if should_be_successful:
        # logout and login newly created account
        logout(test_client)
        login(test_client, new_account_data)

        self.assertEqual(new_account_data.get("email", None), current_user.email)
        self.assertEqual(eval(f"current_user.is_{new_account_role}"), True)
    else:
        self.assertIn(b"cannot create account", response.data)
   
    logout(test_client)
