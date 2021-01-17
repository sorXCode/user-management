from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import InputRequired
from wtforms.fields.html5 import EmailField

class LoginForm(FlaskForm):
    email = EmailField(validators=[InputRequired("Field is required"), ])
    password = PasswordField(validators=[InputRequired("Field is required"),])