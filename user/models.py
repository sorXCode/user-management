from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db, login_manager
from .exceptions import UserExists, UserNotFound, InvalidPassword
from datetime import date

class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String, index=True, unique=True, nullable=False)
    password_hash = db.Column(db.String, nullable=False)
    created_at = db.Column(
        db.TIMESTAMP, server_default=db.func.current_timestamp(), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    is_super_admin = db.Column(db.Boolean, default=False)

    @property
    def password(self):
        raise AttributeError("Password not readable")

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    @classmethod
    def get_user(cls, email):
        return cls.query.filter_by(email=email).first()

    @classmethod
    def create_user(cls, email, password, is_admin=False, is_super_admin=False):
        if cls.get_user(email=email):
            raise UserExists

        user = cls(email=email, is_admin=is_admin, is_super_admin=is_super_admin)
        user.password = password

        db.session.add(user)
        db.session.commit()

        return user

    @classmethod
    def login(cls, email, password):
        user = cls.get_user(email=email)
        if not user:
            raise UserNotFound

        if not user.verify_password(password):
            raise InvalidPassword

        return user

    
    def __repr__(self):
        return f"<User {self.email}"
    
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class Activity(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    count = db.Column(db.Integer, default=1)
    request_date = db.Column(db.DateTime, nullable=False)
    request_type = db.Column(db.String, default="visit")
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    @classmethod
    def log_user(cls, user):
        latest_activity = cls.get_user_latest_activity_for_day(user_id=user.id)

        if latest_activity:
            # incrementing 'count' field transactionally to prevent race-condition
            latest_activity.count = cls.count + 1
        else:
            latest_activity = cls(user_id=user.id)
            latest_activity.request_date = date.today()

        db.session.add(latest_activity)
        db.session.commit()
    
    @classmethod
    def get_user_latest_activity_for_day(cls, user_id):
        return cls.query.filter_by(user_id=user_id, request_date=f"{date.today()} 00:00:00.000000").first()

    @classmethod
    def get_all_activities_for_user(cls, user_id):
        return cls.query.filter_by(user_id=user_id).all()