from flask import (Blueprint, flash, g, redirect, render_template, request,
                   session, url_for)
from flask.views import MethodView, View
from flask_login import current_user, login_required, login_user, logout_user

from .forms import LoginForm, AccountCreationForm, AccountUpdateForm
from .models import Activity, User, Role, Permission
from .utils import access_level
from .exceptions import UserNotFound

user_bp = Blueprint("user_bp", __name__)


@user_bp.before_app_first_request
def create_roles_and_one_superadmin():
    if Role.insert_roles():
        print(f"created roles at app start")
    if Permission.insert_permissions():
        print("inserted permissions")
    if User.create_first_user():
        print(f"created super_admin at app start")


class Homepage(MethodView):
    def get(self):
        if current_user.is_authenticated:
            return redirect(url_for("user_bp.dashboard"))

        login_form = LoginForm()
        return render_template("homepage.html", form=login_form)

    def post(self):
        try:
            login_form = LoginForm()
            if login_form.validate_on_submit():
                # raises exception
                user = User.login(email=login_form.email.data,
                                  password=login_form.password.data)

                login_user(user)
                Activity.log_user(user)
                return redirect(url_for("user_bp.dashboard"))
        except Exception as e:
            flash("".join(e.args))
        return render_template("homepage.html", form=login_form)


class LogoutUser(View):
    methods = ["GET", "POST"]

    def dispatch_request(self):
        logout_user()
        flash("Successfully logged out")
        return redirect(url_for("user_bp.homepage"))


class Dashboard(MethodView):
    decorators = [login_required, ]

    @access_level(levels=["owner", "creator", "super_admin"])
    def get(self, user_email=None):
        if user_email:
            user = User.get_user(email=user_email)
        else:
            user = current_user
        return render_template("dashboard.html", user=user)


class Activities(MethodView):
    decorators = [login_required, ]

    @access_level(levels=["owner", "creator", "super_admin"])
    def get(self, user_id):
        activities, stat = Activity.get_all_activities_for_user(
            user_id=user_id)
        return render_template("activities.html", activities=activities, stat=stat)


class AccountCreation(MethodView):
    decorators = [login_required, ]

    @access_level(levels=["super_admin", "admin"])
    def post(self):
        form = generate_account_creation_form()
        try:
            if form.validate_on_submit():
                create_account = {"super-admin": User.create_super_admin,
                                  "admin": User.create_admin,
                                  "user": User.create_user}
                create_account[form.user_type.data](
                    email=form.email.data.strip(), password=form.password.data)
                flash(f"{form.email.data} account created")
            else:
                flash("cannot create account")
        except Exception as e:
            flash(",".join(e.args))

        return redirect(url_for("user_bp.dashboard"))


class Users(MethodView):
    decorators = [login_required, access_level(
        levels=["super_admin", "admin", ])]

    def get(self):
        form = generate_account_creation_form()
        registered_user = current_user.get_downlines()
        return render_template("users.html", users=registered_user, form=form)

    def delete(self):
        email = request.args.get("user_email", None)
        user = User.get_user(email)
        if user not in current_user.get_downlines():
            return redirect(url_for('user_bp.dashboard'))

        user.delete()
        flash("account deleted")
        return "operation completed"


class ToggleBlockStatus(MethodView):
    decorators = [login_required, ]

    @access_level(levels=["creator", "super_admin"])
    def get(self, user_email):
        user = User.get_user(email=user_email)
        if user:
            user.toggle_block_status()
        return redirect(url_for("user_bp.users"))


class EditUser(MethodView):
    decorators = [login_required, access_level(
        levels=["super_admin", "admin", ])]

    def get(self):
        try:
            user_email = request.args.get('user_email', None)
            user = User.get_user(user_email)
            form = AccountUpdateForm()
            form.email.data = user.email
            return render_template("form.html", form=form,
                                action=f"{url_for('user_bp.edit_user')}?user_email={user_email}",
                                submit_value="Update Account")
        except Exception:
            return "Error!"
    
    def post(self):
        try:
            user_email = request.args.get('user_email', None)
            user = User.get_user(user_email)

            if not user:
                raise UserNotFound
            
            form = AccountUpdateForm()
            if form.validate_on_submit():
                user.update_user(email=form.email.data)
                flash("User profile updated", "success")
            flash("An error occurred", "failed")
        except Exception as e:
            flash(", ".join(e.args), "failed")
        return redirect(url_for("user_bp.users"))
            


def generate_account_creation_form():
    form = AccountCreationForm()

    if current_user.is_super_admin:
        form.user_type.choices = [
            ("super-admin", "super-admin"), ("admin", "admin"), ]
    elif current_user.is_admin:
        form.user_type.choices = [("admin", "admin"), ("user", "user")]

    return form


user_bp.add_url_rule("/", view_func=Homepage.as_view("homepage"))
user_bp.add_url_rule("/dashboard/", view_func=Dashboard.as_view("dashboard"))
user_bp.add_url_rule("/logout/", view_func=LogoutUser.as_view("logout"))
user_bp.add_url_rule(
    "/register/", view_func=AccountCreation.as_view("register"))
user_bp.add_url_rule("/activities/<user_id>/",
                     view_func=Activities.as_view("activities"))
user_bp.add_url_rule("/users/",
                     view_func=Users.as_view("users"))
user_bp.add_url_rule("/users/edit", view_func=EditUser.as_view("edit_user"))
user_bp.add_url_rule("/users/<user_email>/toggle",
                     view_func=ToggleBlockStatus.as_view("toggle_block_status"))
user_bp.add_url_rule("/users/<user_email>",
                     view_func=Dashboard.as_view("user_dashboard"))
