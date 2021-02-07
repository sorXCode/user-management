from flask import url_for


def logout(test_client):
    return test_client.get(url_for("user_bp.logout"), follow_redirects=True)


def login(test_client, credentials):
    return test_client.post(url_for("user_bp.homepage"),
                            data=credentials, follow_redirects=True)


def register(test_client, credentials):
    return test_client.post(url_for("user_bp.register"),
                            data=credentials, follow_redirects=True)


def create_team(test_client, team_name, description):
    return test_client.post(url_for("team_bp.create_team"),
                            data={"name": team_name,
                                  "description": description},
                            follow_redirects=True)


def view_team(test_client, team_name):
    return test_client.get(url_for("team_bp.team_view", team_name=team_name), follow_redirects=True)


def view_teams_list(test_client):
    return test_client.get(url_for("team_bp.teams"), follow_redirects=True)


def update_team(test_client, team_name, **kwargs):
    data = {"name": kwargs.get("name", None),
            "description": kwargs.get("description", None)
            }
    return test_client.post(url_for("team_bp.team_view", team_name=team_name),
                            data=data, follow_redirects=True)

def add_user_to_team(test_client, team_name, user_email):
    data = {"users": [user_email,]}
    return test_client.post(url_for("team_bp.add_team_user", team_name=team_name),
                            data=data, follow_redirects=True)

def toggle_team_status(test_client, team_name):
    return test_client.put(url_for("team_bp.toggle_team_status", team_name=team_name),
                            follow_redirects=True)
