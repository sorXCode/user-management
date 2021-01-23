from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField
from wtforms.validators import InputRequired
from wtforms.fields.html5 import EmailField

class LoginForm(FlaskForm):
    email = EmailField(validators=[InputRequired("Field is required"), ])
    password = PasswordField(validators=[InputRequired("Field is required"),])

class AccountCreationForm(FlaskForm):
    email = EmailField(validators=[InputRequired("Field is required"), ])
    password = PasswordField(validators=[InputRequired("Field is required"),])
    user_type = SelectField(choices=[], validators=[InputRequired("Field is required"),])
