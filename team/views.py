from flask import (Blueprint, flash, g, redirect,
                   render_template, request, url_for)
from flask.views import MethodView, View
from flask_login import current_user, login_required, login_user, logout_user
from .forms import TeamCreationForm, TeamSearchForm
from .models import Team

team_bp = Blueprint("team_bp", __name__)


class TeamCreation(MethodView):
    decorators = [login_required, ]

    def post(self):
        form = TeamCreationForm()
        try:
            if form.validate_on_submit():

                Team.create_team(
                    name=form.name.data,
                    description=form.description.data,
                    creator_id=current_user.id)
                
                flash(f"{form.name.data} Team created", 'success')
            else:
                flash("cannot create team", 'failed')
        except Exception as e:
            flash(",".join(e.args))
        
        return redirect(url_for("team_bp.teams"))


class TeamsList(MethodView):
    decorators = [login_required, ]

    def get(self):
        teams = current_user.get_all_teams()
        form = TeamCreationForm()
        return render_template("teams.html", form=form, teams=teams)
    
class TeamView(MethodView):
    decorators = [login_required,]

    def get(self, team_name=None):
        if team_name:
            team = Team.get_team_by_name(name=team_name)
            users_in_team = [user_team.team_member for user_team in team.user_team.all()]
            return render_template("team.html", users=users_in_team, team=team)
        return redirect(url_for("team_bp.teams"))

class TeamSearch(MethodView):
    decorators = [login_required, ]

    def post(self):
        form = TeamSearchForm()
        team = None

        if form.validate_on_submit():
            team = Team.search_by_part_name(form.name.data)
        return render_template("teamsearch_result.html", team=team)

team_bp.add_url_rule("/teams", view_func=TeamsList.as_view("teams"))
team_bp.add_url_rule("/teams/search", view_func=TeamSearch.as_view("create_team"))
team_bp.add_url_rule("/teams/<team_name>", view_func=TeamView.as_view("team_view"))
team_bp.add_url_rule("/teams", view_func=TeamCreation.as_view("create_team"))