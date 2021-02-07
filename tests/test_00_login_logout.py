from . import BaseTestCase, db
from user.models import User, Role, UserRole, Permission
from flask import url_for
from flask_login import current_user
from .utils import logout, login, register

class TestLogin(BaseTestCase):
    # setup default db, roles, users

    def setUp(self):
        super().setUp()
        # Dropping and creating tables on signup test\
        # to ensure retest success
        db.drop_all()
        db.create_all()
        Role.insert_roles()
        Permission.insert_permissions()
        User.create_first_user()


        # create default accounts for tests
        for role in self.user_data:
            
            if role =="user":
                continue

            user = {"email": self.user_data[role]["email"]}
            user = User(**user)
            user.password = self.user_data[role]["password"]
            user.user_roles.append(UserRole(role=eval(f"Role.get_{role}_role()"), user=user))
            db.session.add(user)

        db.session.commit()
    

    def test_load_homepage(self):
        response = self.test_client.get(
            url_for("user_bp.homepage"), follow_redirects=True)
        
        # assert template loaded successfully
        self.assertEqual(response.status_code, 200)
        # check login form fields
        self.assertIn(b'name="email"', response.data)
        self.assertIn(b'name="password"', response.data)
        self.assertIn(b'type="submit"', response.data)

    def test_login_logout(self):
        # keeping request context open to check user properties after login
        with self.test_client as test_client:
            
            response = login(test_client, self.user_data["super_admin"])
            # assert template loaded successfully
            self.assertEqual(response.status_code, 200)

            # check relative "LOGOUT" link in response
            logout_link = url_for("user_bp.logout")
            self.assertIn(logout_link, response.data.decode('utf-8'))

            self.assertEqual(self.user_data["super_admin"]["email"], current_user.email)

            # logout user
            response = logout(test_client)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(False, current_user.is_authenticated)
