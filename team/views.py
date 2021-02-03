from flask import (Blueprint, flash, g, redirect, render_template, request, url_for)
from flask.views import MethodView, View
from flask_login import current_user, login_required, login_user, logout_user

team_bp = Blueprint("team_bp", __name__)
