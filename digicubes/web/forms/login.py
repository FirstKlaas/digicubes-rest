from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, SubmitField, validators
from wtforms.widgets import html_params


def materialize_input(field, **kwargs):
    field_id = kwargs.pop("id", field.id)
    field_type = kwargs.get("type", "text")

    attributes = {
        "id" : field_id, 
        "type" : field_type,
        "class" : "validate",
        "placeholder" : "Enter your login"
    }
    

    html = [f"<input {html_params(**attributes)}></input>"]
    return "".join(html)

def materialize_submit(field, **kwargs):
    field_id = kwargs.pop("id", field.id)
    field_type = kwargs.get("type", "submit")
    label = kwargs.get("label", "Ok")
    icon = kwargs.get("icon", "send")

    button_attrs = {
        "id" : field_id, 
        "type" : field_type,
        "class" : "btn blue waves-effect waves-light"
    }

    html = [f"<button {html_params(**button_attrs)}>{label}"]
    html.append(f"<i class='material-icons right'>{icon}</i>")
    html.append("</button>")
    return "".join(html)

class LoginForm(FlaskForm):
    login = StringField("Login", widget=materialize_input, validators=[validators.InputRequired()])
    password = PasswordField("Password", validators=[validators.InputRequired()])
    submit = SubmitField("Login", widget=materialize_submit)
