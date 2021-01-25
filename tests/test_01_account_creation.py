from . import BaseTestCase, db, fake
from flask import url_for
from flask_login import current_user
from .utils import login, logout, register


class TestAccountCreation(BaseTestCase):
    another_super_admin = {"email": fake.email(
    ), "password": fake.text(), "user_type": "super-admin"}
    admin_one = {"email": fake.email(), "password": fake.text(),
                 "user_type": "admin"}
    user_one = {"email": fake.email(), "password": fake.text(),
                "user_type": "user"}

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
            create_account(self=self, test_client=test_client, user_data=self.user_data,
                           user_role="super_admin", new_account_data=self.another_super_admin, new_account_role="super_admin")

    def test_super_admin_create_admin(self):
        with self.test_client as test_client:
            create_account(self=self, test_client=test_client, user_data=self.user_data,
                           user_role="super_admin", new_account_data=self.admin_one, new_account_role="admin")

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


def create_account(self, test_client, user_data, user_role, new_account_data, new_account_role):
    login(test_client, user_data)
    self.assertEqual(eval(f"current_user.is_{user_role}()"), True)

    # create new_user
    register(test_client, new_account_data)

    # logout and login newly created account
    logout(test_client)
    login(test_client, new_account_data)

    self.assertEqual(new_account_data.get("email", None), current_user.email)
    self.assertEqual(eval(f"current_user.is_{new_account_role}()"), True)
    logout(test_client)
