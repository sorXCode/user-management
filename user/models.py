from flask_login import UserMixin, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from app import db, login_manager
from .exceptions import UserExists, UserNotFound, InvalidPassword, Unauthorized
from datetime import date
from sqlalchemy.orm import backref

class Permission:
    USER = 0
    ADMIN = 1
    SUPER_ADMIN = 10


class Role(db.Model):
    __tablename__ = 'roles'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(60), unique=True, nullable=False)
    permissions = db.Column(db.Integer)
    users = db.relationship('User', backref='role', lazy='dynamic')

    
    @classmethod
    def insert_roles(cls):
        roles = {
            "user": Permission.USER,
            "admin": Permission.ADMIN,
            "super_admin": Permission.SUPER_ADMIN,
        }
        created_role = False
        for role in roles:
            role_object = cls.query.filter_by(name=role).first()
            if role_object:
                continue
            role_object = cls(name=role, permissions=roles[role])
            db.session.add(role_object)
            created_role = True
        db.session.commit()
        return created_role


class Relation(db.Model):
    __tablename__ = "Relations"
    id = db.Column(db.Integer, primary_key=True)
    parent_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    child_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    @classmethod
    def establish_relationship(cls, parent_id, child_id):
        link = cls(parent_id=parent_id, child_id=child_id)
        db.session.add(link)
        db.session.commit()
        return link
    
    def __repr__(self):
        return f"{self.parent.email} -> {self.child.email}"

class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String, index=True, unique=True, nullable=False)
    password_hash = db.Column(db.String, nullable=False)
    created_at = db.Column(
        db.TIMESTAMP, server_default=db.func.current_timestamp(), nullable=False)
    updated_on = db.Column(db.DateTime, server_default=db.func.now(), server_onupdate=db.func.now(), nullable=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    upline = db.relationship('Relation', backref='upline', foreign_keys="[Relation.child_id]", uselist=False, lazy=True)
    downlines = db.relationship('Relation', backref='downline', foreign_keys="[Relation.parent_id]", lazy='dynamic')

    
    # downline_id = db.Column(db.Integer, db.ForeignKey('creation.id'))
    # upline = db.Column(db.Integer)

    @classmethod
    def first_user(cls):
        if cls.query.filter_by().first():
           return None
           
        first_user_role = "super_admin"
        user = cls(email="root@root.com")
        user.password = "root"
        user.role = Role.query.filter_by(name=first_user_role).first()
        db.session.commit()
        return True
        

    # @property
    # def downlines(self):
    #     return [int(x) for x in self._downlines(";")]

    # @downlines.setter
    # def downlines(self, value):
    #     if self._downlines:
    #         self._downlines = self._downlines + f";{value}"
    #     else:
    #         self._downlines = f"{value}"

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
        if not (current_user.is_admin() or current_user.is_super_admin()):
            raise Unauthorized

        if cls.get_user(email=email):
            raise UserExists

        user = cls(email=email, is_admin=is_admin,
                   is_super_admin=is_super_admin)

        user.password = password

        # give created user a role
        if is_super_admin:
            user.role = Role.query.filter_by(name="super_admin").first()
        elif is_admin:
            user.role = Role.query.filter_by(name="admin").first()
        else:
            user.role = Role.query.filter_by(name="user").first()

        # add and commit new user to get an id which would be used to link the user to its creator
        db.session.add(user)
        db.session.commit()

        Relation.establish_relationship(parent_id=current_user.id, child_id=user.id)

        return user

    @classmethod
    def create_super_admin(cls, email, password):
        if current_user.is_super_admin():
            return cls.create_user(email=email, password=password, is_super_admin=True)
        raise Unauthorized

    @classmethod
    def create_admin(cls, email, password):
        if current_user.is_admin() or current_user.is_super_admin():
            return cls.create_user(email=email, password=password, is_admin=True)
        raise Unauthorized

    @classmethod
    def login(cls, email, password):
        user = cls.get_user(email=email)
        if not user:
            raise UserNotFound

        if not user.verify_password(password):
            raise InvalidPassword

        return user

    def can(self, permissions):
        return self.role is not None and \
            (self.role.permissions & permissions) == permissions

    def is_admin(self):
        return self.can(Permission.ADMIN)

    def is_super_admin(self):
        return self.can(Permission.SUPER_ADMIN)

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
