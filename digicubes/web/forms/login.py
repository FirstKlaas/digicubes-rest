from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, validators


class LoginForm(FlaskForm):
    login = StringField("Login", validators=[validators.InputRequired()])
    password = PasswordField("Password", validators=[validators.InputRequired()])
