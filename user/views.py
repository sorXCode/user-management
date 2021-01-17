from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from flask.views import MethodView
from flask_login import login_user

from .models import User
from .forms import LoginForm

user_bp = Blueprint("user_bp", __name__)

class Homepage(MethodView):
    def get(self):
        login_form = LoginForm()
        return render_template("homepage.html", form=login_form)
    
    def post(self):
        try:
            login_form = LoginForm()
            if login_form.validate_on_submit():
                # raises exception
                user = User.login(email=login_form.email.data, password=login_form.password.data)
                
                login_user(user)
                return redirect("/dashboard")
        except Exception as e:
            flash("".join(e.args))
        return render_template("homepage.html", form=login_form)
            
        
        

class Dashboard(MethodView):
    def get(self):
        # login_form = 
        return "Hello"



user_bp.add_url_rule("/", view_func=Homepage.as_view("homepage"))
user_bp.add_url_rule("/dashboard", view_func=Dashboard.as_view("dashboard"))