from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import InputRequired


class BaseTeamForm(FlaskForm):
    name = StringField(validators=[InputRequired("Field is required"), ])

class TeamCreationForm(BaseTeamForm):
    description = StringField(validators=[InputRequired("Field is required"), ])


class TeamSearchForm(BaseTeamForm):
    pass
