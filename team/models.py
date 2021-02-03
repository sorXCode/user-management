from app import db
from flask_login import current_user
class Team(db.Model):
    __tablename__ = "teams"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    description = db.Column(db.String)
    created_by = db.Column(db.Integer, db.ForeignKey("users.id"))
    created_at = db.Column(db.TIMESTAMP, server_default=db.func.current_timestamp(), nullable=False)
    updated_at = db.Column(db.TIMESTAMP, server_default=db.func.current_timestamp(), nullable=False)
    user_team = db.relationship("UserTeam", backref="team", lazy="dynamic")

    @classmethod
    def create_team(cls, name, description, creator_id):
        team = cls(name=name, description=description)
        team.created_by = creator_id
        team.save()
        UserTeam.admit_user_to_team(team=team, user_id=creator_id, admitted_by=creator_id)
        return team
    

    def save(self):
        db.session.add(self)
        db.session.commit()


class UserTeam(db.Model):
    __tablename__ = "user_teams"
    id = db.Column(db.Integer, primary_key=True)
    team_id = db.Column(db.Integer, db.ForeignKey("teams.id"))
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    admitted_by = db.Column(db.Integer, db.ForeignKey("users.id"))

    @classmethod
    def admit_user_to_team(cls, team, user_id, admitted_by):
        user_team = cls(team=team, user_id=user_id, admitted_by=admitted_by)
        user_team.save()
        return user_team

    def save(self):
        db.session.add(self)
        db.session.commit()