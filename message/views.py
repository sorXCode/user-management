from flask import (Blueprint, flash, g, redirect, render_template, request,
                   session, url_for)
from flask.views import MethodView
from user.utils import access_level
from .models import Message
from flask_login import current_user, login_required
from user.models import User


message_bp = Blueprint("message_bp", __name__)


class Messages(MethodView):
    decorators = [login_required, access_level(["child", "creator", ])]

    def get(self, user_email):
        user_b = User.get_user(user_email)
        messages = Message.get_chat_history(
            user_a_id=current_user.id, user_b_id=user_b.id)
        return render_template("chat.html", messages=messages, user_email=user_email)

    def post(self, user_email):
        receiver = User.get_user(user_email)
        message = request.args.get("message")
        if message:
            message = Message.send_message(receiver, current_user, message)

        return redirect(url_for("message_bp.message", user_email=user_email), code=303)

class RecentConversation(MethodView):
    decorators = [login_required, ]

    def get(self):
        conversations = Message.get_conversations(user_id=current_user.id)
        return render_template("messages.html", conversations=conversations)

message_bp.add_url_rule("/messages",
                        view_func=RecentConversation.as_view("recent_messages"))
message_bp.add_url_rule("/messages/<user_email>",
                        view_func=Messages.as_view("message"))
