from flask import (Blueprint, flash, g, redirect, render_template, request,
                   session, url_for)
from flask.views import MethodView
from user.utils import access_level
from .models import Message
from flask_login import current_user, login_required


class Messages(MethodView):
    decorators = [login_required, access_level(["owner", "creator",])]

    def get(self):
        messages = Message.get_conversation_history(receiver=current_user, sender=)