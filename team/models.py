from app import db
from flask_login import current_user
from .exceptions import TeamExists, TeamNotFound, UserExistInTeam


class Team(db.Model):
    __tablename__ = "teams"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False, unique=True)
    description = db.Column(db.String)
    created_by = db.Column(db.Integer, db.ForeignKey("users.id"))
    created_at = db.Column(
        db.TIMESTAMP, server_default=db.func.current_timestamp(), nullable=False)
    updated_at = db.Column(
        db.TIMESTAMP, server_default=db.func.current_timestamp(), nullable=False)
    is_active = db.Column(
        db.Boolean(), default=True
    )
    user_team = db.relationship("UserTeam", backref="team", lazy='dynamic', cascade="all, delete",)

    @classmethod
    def get_team_by_name(cls, name):
        name = name.strip()
        team = cls.query.filter_by(name=name).first()
        if not team:
            raise TeamNotFound
        return team

    @classmethod
    def search_team_by_part_name(cls, part_name):
        pass

    @classmethod
    def create_team(cls, name, description, creator_id):
        name = name.strip()
        description = description.strip()

        if cls.query.filter_by(name=name).first():
            raise TeamExists

        team = cls(name=name, description=description)
        team.created_by = creator_id
        team.save()
        UserTeam.admit_user_to_team(
            team=team, user_id=creator_id, admitted_by=creator_id)
        return team

    def save(self):
        db.session.add(self)
        db.session.commit()

    def get_all_users(self):
        return list(set(user_team.team_member for user_team in self.user_team.all()))

    def toggle_status(self):
        self.is_active = not self.is_active
        self.save()

    def delete(self):
        db.session.delete(self)
        db.session.commit()


class UserTeam(db.Model):
    __tablename__ = "user_teams"
    id = db.Column(db.Integer, primary_key=True)
    team_id = db.Column(db.Integer, db.ForeignKey(
        "teams.id", ondelete="CASCADE"))
    user_id = db.Column(db.Integer, db.ForeignKey(
        "users.id", ondelete="CASCADE"))
    admitted_by = db.Column(db.Integer, db.ForeignKey("users.id"))

    @classmethod
    def is_user_in_team(cls, team, user_id):
        return bool(cls.query.filter_by(team=team, user_id=user_id).first())

    @classmethod
    def admit_user_to_team(cls, team, user_id, admitted_by):
        if cls.is_user_in_team(team=team, user_id=user_id):
            raise UserExistInTeam
        user_team = cls(team=team, user_id=user_id, admitted_by=admitted_by)
        user_team.save()
        return user_team

    @classmethod
    def remove_user_from_team(cls, team, user_id):
        entry = cls.query.filter_by(team=team, user_id=user_id).first()
        if entry:
            entry.delete()

    def save(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()
