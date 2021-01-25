from flask import url_for


def logout(test_client):
    return test_client.get(url_for("user_bp.logout"), follow_redirects=True)


def login(test_client, credentials):
    return test_client.post(url_for("user_bp.homepage"),
                     data=credentials, follow_redirects=True)


def register(test_client, credentials):
    return test_client.post(url_for("user_bp.register"),
                     data=credentials, follow_redirects=True)
