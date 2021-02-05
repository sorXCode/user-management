from flask import (Blueprint, flash, g, redirect,
                   render_template, request, url_for)
from flask.views import MethodView, View
from flask_login import current_user, login_required, login_user, logout_user
from .forms import TeamCreationForm, TeamUpdateForm, TeamSearchForm, AddUserToTeamForm
from .models import Team, UserTeam
from .exceptions import UserExistInTeam

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
            
            update_team_form = TeamUpdateForm()
            update_team_form.name.data = team.name
            update_team_form.description.data = team.description

            add_user_form = generate_add_user_to_team_form(team=team)
            
            users_in_team = team.get_all_users()
            return render_template("team.html", users=users_in_team, team=team, update_team_form=update_team_form, add_user_form=add_user_form)
        return redirect(url_for("team_bp.teams"))
    
    def post(self, team_name):
        form = TeamUpdateForm()

        if form.validate_on_submit():
            team = Team.get_team_by_name(name=team_name)
            
            team.name = form.name.data
            team.description = form.description.data
            team.save()

            flash("Team updated", 'success')
            return redirect(url_for("team_bp.team_view", team_name=team.name))
        flash('Team update failed', 'failed')
        return redirect(url_for("team_bp.teams"))

class AddTeamUsers(MethodView):
    decorators = [login_required, ]

    def post(self, team_name=None):
        team = Team.get_team_by_name(team_name)
        form = generate_add_user_to_team_form(team=team)

        if form.validate_on_submit():
            count = 0
            for user in form.users.data:
                try:
                    UserTeam.admit_user_to_team(team=team, user_id=user.id, admitted_by=current_user.id)
                    count += 1
                except Exception as e:
                    flash(f"{user.email} {', '.join(e.args)}", 'failed')

            flash(f"{count} users added", "success")
        return redirect(url_for("team_bp.team_view", team_name=team_name))
class RemoveTeamUser(MethodView):
    decorators = [login_required,]

    def delete(self, team_name=None, user_id=None):
        team = Team.get_team_by_name(team_name)
        UserTeam.remove_user_from_team(team=team, user_id=user_id)
        return "Operation completed"

class TeamSearch(MethodView):
    decorators = [login_required, ]

    def post(self):
        form = TeamSearchForm()
        team = None

        if form.validate_on_submit():
            team = Team.search_by_part_name(form.name.data)
        return render_template("teamsearch_result.html", team=team)

class ToggleTeamStatus(MethodView):
    decorators = [login_required, ]

    def put(self):
        team_name = request.args["team_name"]
        team = Team.get_team_by_name(name=team_name)
        team.toggle_status()
        flash(f"{team_name} {'activated' if team.is_active else 'deactivated'}")
        return "operation completed"

class DeleteTeam(MethodView):
    decorators = [login_required, ]

    def delete(self):
        team_name = request.args["team_name"]
        team = Team.get_team_by_name(name=team_name)
        team.delete()
        flash(f"{team_name} deleted")
        return "operation completed"

def generate_add_user_to_team_form(team):
    def get_downlines_not_in_team():
        registered_users = current_user.get_downlines()
        team_users = team.get_all_users()
        return filter(lambda user: user not in team_users, registered_users)
    
    form = AddUserToTeamForm()
    form.users.choices = [(user.email, user.email,) for user in get_downlines_not_in_team()]
    return form

team_bp.add_url_rule("/teams", view_func=TeamsList.as_view("teams"))
team_bp.add_url_rule("/teams", view_func=TeamCreation.as_view("create_team"))
team_bp.add_url_rule("/teams/toggle", view_func=ToggleTeamStatus.as_view("toggle_team_status"))
team_bp.add_url_rule("/teams/search", view_func=TeamSearch.as_view("search_team"))
team_bp.add_url_rule("/teams/delete", view_func=DeleteTeam.as_view("delete_team"))
team_bp.add_url_rule("/teams/<team_name>", view_func=TeamView.as_view("team_view"))
team_bp.add_url_rule("/teams/<team_name>/users/<user_id>", view_func=RemoveTeamUser.as_view("remove_team_user"))
team_bp.add_url_rule("/teams/<team_name>/users", view_func=AddTeamUsers.as_view("add_team_user"))