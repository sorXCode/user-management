from functools import wraps
from flask_login import current_user, logout_user
from team.models import Team


def is_team_member(team: Team):
    """
    Decorator to check if user is in team
    """
    def decorated_view(func):
        @wraps(func)
        def check_user_membership(*args, **kwargs):
            if current_user in team.get_all_users():
                return func(*args, **kwargs)
            else:
                flash("You're never here!")
                logout_user()
                return current_user.login_manager.unauthorized()
        return check_user_membership
    return decorated_view
