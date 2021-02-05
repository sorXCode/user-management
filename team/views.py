from flask import (Blueprint, flash, g, redirect,
                   render_template, request, url_for)
from flask.views import MethodView, View
from flask_login import current_user, login_required, login_user, logout_user
from .forms import TeamCreationForm, TeamSearchForm
from .models import Team, UserTeam

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
            
            form = TeamCreationForm()
            form.name.data = team.name
            form.description.data = team.description

            users_in_team = [user_team.team_member for user_team in team.user_team.all()]
            return render_template("team.html", users=users_in_team, team=team, form=form)
        return redirect(url_for("team_bp.teams"))
    
    def post(self, team_name):
        form = TeamCreationForm()

        if form.validate_on_submit():
            team = Team.get_team_by_name(name=team_name)
            
            team.name = form.name.data
            team.description = form.description.data
            team.save()

            flash("Team updated", 'success')
            return redirect(url_for("team_bp.team_view", team_name=team.name))
        flash('Team update failed', 'failed')
        return redirect(url_for("team_bp.teams"))

class RemoveTeamMember(MethodView):
    decorators = [login_required,]

    def delete(self, team_id=None, user_id=None):
        UserTeam.remove_user_from_team(team_id=team_id, user_id=user_id)
        return "Operation completed"

class TeamSearch(MethodView):
    decorators = [login_required, ]

    def post(self):
        form = TeamSearchForm()
        team = None

        if form.validate_on_submit():
            team = Team.search_by_part_name(form.name.data)
        return render_template("teamsearch_result.html", team=team)



team_bp.add_url_rule("/teams", view_func=TeamsList.as_view("teams"))
team_bp.add_url_rule("/teams", view_func=TeamCreation.as_view("create_team"))
team_bp.add_url_rule("/teams/search", view_func=TeamSearch.as_view("search_team"))
team_bp.add_url_rule("/teams/<team_name>", view_func=TeamView.as_view("team_view"))
team_bp.add_url_rule("/teams/<int:team_id>/<int:user_id>", view_func=RemoveTeamMember.as_view("remove_team_member"))