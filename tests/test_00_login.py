from . import BaseTestCase, db
from user.models import User
from flask import url_for
from flask_login import current_user

class TestLogin(BaseTestCase):

    def setUp(self):
        super().setUp()
        # Dropping and creating tables on signup test\
        # to ensure retest success
        db.drop_all()
        db.create_all()
        # create default user for tests
        super_admin = {"email": "root@root.com", "is_super_admin": True}
        super_admin = User(**super_admin)
        super_admin.password = "root"
        db.session.add(super_admin)
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
            
            response = test_client.post(url_for("user_bp.homepage"), data=self.user_data, follow_redirects=True)
            # assert template loaded successfully
            self.assertEqual(response.status_code, 200)

            # check relative "LOGOUT" link in response
            logout_link = url_for("user_bp.logout")
            self.assertIn(logout_link, response.data.decode('utf-8'))

            self.assertEqual(self.user_data["email"], current_user.email)

            # logout user
            response = test_client.get(logout_link, follow_redirects=True)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(False, current_user.is_authenticated)
