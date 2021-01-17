from flask import (Blueprint, flash, g, redirect, render_template, request,
                   session, url_for)
from flask.views import MethodView, View
from flask_login import current_user, login_required, login_user, logout_user

from .forms import LoginForm
from .models import User

user_bp = Blueprint("user_bp", __name__)


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
        return render_template("dashboard.html")


user_bp.add_url_rule("/", view_func=Homepage.as_view("homepage"))
user_bp.add_url_rule("/dashboard", view_func=Dashboard.as_view("dashboard"))
user_bp.add_url_rule("/logout", view_func=LogoutUser.as_view("logout"))
