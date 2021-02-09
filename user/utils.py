from functools import wraps
from flask import current_app, flash
from flask_login import current_user, logout_user
from .models import User

def access_level(levels):
    """
    Decorator for access level control
    """
    def decorated_view(func):
        @wraps(func)
        def user_permitted(*args, **kwargs):
            user = User.get_user(kwargs.get("user_email", None))

            access = {"super_admin": current_user.is_super_admin,
                        "admin": current_user.is_admin,
                        }
            if user:
                access["owner"] = user.id==current_user.id
                access["creator"] = user.upline.id==current_user.id
                access["child"] = current_user in user.get_downlines()

            for user_level in levels:
                if access.get(user_level, "default"):
                    return func(*args, **kwargs)
            else:
                logout_user()
                flash("You're not authorized to view this page!")
                return current_app.login_manager.unauthorized()
        return user_permitted
    return decorated_view
    