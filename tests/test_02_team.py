from . import BaseTestCase, db, fake
from flask import url_for
from flask_login import current_user
from .utils import (login, logout, create_team, view_team,
                    view_teams_list, update_team, add_user_to_team, toggle_team_status)
from .teams import *
from random import choice
from user.models import User
from team.models import Team


class TestTeamCreation(BaseTestCase):
    def test_super_admin_create_team(self):
        with self.test_client as test_client:
            self.create_random_team(
                test_client=test_client, current_user_role="super_admin")

    def test_admin_create_team(self):
        with self.test_client as test_client:
            self.create_random_team(test_client=test_client, current_user_role="admin")

    def test_user_create_team(self):
        with self.test_client as test_client:
            self.create_random_team(
                test_client=test_client, current_user_role="user", should_be_successful=False)

    def create_random_team(self, test_client, current_user_role, should_be_successful=True):
        user_data = self.user_data[current_user_role]
        team_name = fake.name()
        team_description = fake.text()

        login(test_client, user_data)
        self.assertEqual(eval(f"current_user.is_{current_user_role}"), True)

        create_team(test_client, team_name=team_name,
                    description=team_description)
        response = view_teams_list(test_client)

        if should_be_successful:
            self.assertIn(team_name, str(response.data))
        else:
            self.assertNotIn(team_name, str(response.data))

        logout(test_client)


class TestAddUserToTeam(BaseTestCase):
    def test_super_admin_add_downline_to_team(self):
        with self.test_client as test_client:
            # adding created self.user_data["user"] account for future tests
            self.add_user_to_team(test_client=test_client, current_user_role="super_admin")
    
    def test_super_admin_add_non_downline_to_team(self):
        with self.test_client as test_client:
            self.add_user_to_team(test_client=test_client, current_user_role="super_admin",
                                    is_downline=False, should_be_successful=False)

    def test_admin_add_downline_to_team(self):
        with self.test_client as test_client:
            self.add_user_to_team(test_client=test_client, current_user_role="admin", user_to_add=self.user_data["user"]["email"])
    
    def test_admin_add_non_downline_to_team(self):
        with self.test_client as test_client:
            self.add_user_to_team(test_client=test_client, current_user_role="admin",
                                    is_downline=False, should_be_successful=False)
    
    def test_user_add_user_to_team(self):
        with self.test_client as test_client:
            self.add_user_to_team(test_client=test_client, current_user_role="user",
                                    is_downline=False, should_be_successful=False)
    
    def add_user_to_team(self, test_client, current_user_role, user_to_add=None, is_downline=True, should_be_successful=True):
        login(test_client, self.user_data[current_user_role])
        self.assertEqual(eval(f"current_user.is_{current_user_role}"), True)

        team = get_current_user_random_team()
        user_to_add = user_to_add or get_current_user_random_downline() if is_downline else fake.email()

        response = add_user_to_team(test_client=test_client, team_name=team.name, user_email=user_to_add)

        if should_be_successful:
            self.assertIn(user_to_add, str(response.data))
        else:
            self.assertNotIn(user_to_add, str(response.data))

class TestToggleTeamStatus(BaseTestCase):
    def test_super_admin_deactivate_team(self):
        with self.test_client as test_client:
            self.deactivate_team(test_client=test_client, current_user_role="super_admin")
    
    def test_admin_deactivate_team(self):
        with self.test_client as test_client:
            self.deactivate_team(test_client=test_client, current_user_role="admin", should_be_successful=False)
    
    # def test_user_deactivate_team(self):
    #     with self.test_client as test_client:
    #         self.deactivate_team(test_client=test_client, current_user_role="user", should_be_successful=False)
    
    def deactivate_team(self, test_client, current_user_role, should_be_successful=True):
        login(test_client, self.user_data[current_user_role])

        self.assertEqual(eval(f"current_user.is_{current_user_role}"), True)
        team = get_current_user_random_team()
        team_is_active = team.is_active
        team_name = team.name
        response = view_teams_list(test_client)
        
        if should_be_successful:
            self.assertIn("ctivate", str(response.data))
            for click in range(2):
                toggle_team_status(test_client, team_name)
                updated_team = Team.get_team_by_name(team_name)
                
                if click%2:
                    self.assertEqual(team_is_active, updated_team.is_active)
                else:
                    self.assertNotEqual(team_is_active, updated_team.is_active)
        else:
            self.assertNotIn('ctivate', str(response.data))
        logout(test_client)




class TestTeamUpdate(BaseTestCase):
    def test_super_admin_update_team(self):
        with self.test_client as test_client:
            self.update_team(test_client=test_client, current_user_role="super_admin")
    
    def test_admin_update_team(self):
        with self.test_client as test_client:
            self.update_team(test_client=test_client, current_user_role="admin")

    def update_team(self, test_client, current_user_role, should_be_successful=True):
        login(test_client, self.user_data[current_user_role])
        response = view_teams_list(test_client)
        team = get_current_user_random_team()
        team_name = team.name
        view_team(test_client, team_name)

        new_team_name = fake.name()
        new_team_description = fake.text()

        response = update_team(test_client=test_client,
                               team_name=team_name,
                               name=new_team_name,
                               description=new_team_description)
        if should_be_successful:
            self.assertIn(new_team_name, str(response.data))
        else:
            self.assertNotIn(new_team_name, str(response.data))

        logout(test_client)



def get_current_user_random_team():
    _current_user = refetch_current_user()
    return choice(list(_current_user.get_all_teams()))

def get_current_user_random_downline():
    _current_user = refetch_current_user()
    return choice(_current_user.get_downlines()).email

def refetch_current_user():
    # need to fetch user out of context
    return User.get_user_by_id(current_user.id)

