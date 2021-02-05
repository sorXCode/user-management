from flask_wtf import FlaskForm
from wtforms import StringField, SelectMultipleField
from wtforms.validators import InputRequired
from user.models import User


class BaseTeamForm(FlaskForm):
    name = StringField(validators=[InputRequired("Field is required"), ])

class TeamCreationForm(BaseTeamForm):
    description = StringField(validators=[InputRequired("Field is required"), ])

TeamUpdateForm = TeamCreationForm
class TeamSearchForm(BaseTeamForm):
    pass


class AddUserToTeamForm(FlaskForm):
    users = SelectMultipleField()

    @staticmethod
    def validate_users(form, field):
        obj = []
        
        for choice in field:
            obj.append(User.get_user(email=choice.data))
        
        form.users.data = obj