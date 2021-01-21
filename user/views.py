from flask import (Blueprint, flash, g, redirect, render_template, request,
                   session, url_for)
from flask.views import MethodView, View
from flask_login import current_user, login_required, login_user, logout_user

from .forms import LoginForm, AccountCreationForm
from .models import Activity, User, Role

user_bp = Blueprint("user_bp", __name__)


@user_bp.before_app_first_request
def create_roles_and_one_super_admin():
    if Role.insert_roles():
        print(f"created roles at app start")
    if User.first_user():
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

    def get(self):
        form = generate_account_creation_form()
        return render_template("dashboard.html", form=form)

class Activities(MethodView):
    decorators = [login_required, ]

    def get(self, user_id):
        activities = Activity.get_all_activities_for_user(user_id=user_id)
        return render_template("activities.html")


class AccountCreation(MethodView):
    decorators = [login_required, ]

    def post(self):
        form = generate_account_creation_form()
        try:
            if form.validate_on_submit():
                create_account = {"super-admin": User.create_super_admin,
                                "admin": User.create_admin,
                                "user": User.create_user}
                create_account[form.user_type.data](email=form.email.data, password=form.password.data)
                flash(f"{form.email.data} account created")
            else:
                flash("cannot create account")
        except Exception as e:
            flash(",".join(e.args))

        return redirect(url_for("user_bp.dashboard"))


def generate_account_creation_form():
    form = AccountCreationForm()

    if current_user.is_super_admin:
        form.user_type.choices = [("super-admin", "super-admin"), ("admin", "admin"),]
    elif current_user.is_admin:
        form.user_type.choices = [("admin", "admin"), ("user", "user")]
    
    return form

user_bp.add_url_rule("/", view_func=Homepage.as_view("homepage"))
user_bp.add_url_rule("/dashboard/", view_func=Dashboard.as_view("dashboard"))
user_bp.add_url_rule("/logout/", view_func=LogoutUser.as_view("logout"))
user_bp.add_url_rule("/register/", view_func=AccountCreation.as_view("register"))
user_bp.add_url_rule("/activities/<user_id>/", view_func=Activities.as_view("activities"))
