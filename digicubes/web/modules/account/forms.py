"""
Some forms to be used with the wtforms package.
"""
import logging

from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, SubmitField, Field, validators
from wtforms.widgets import html_params

logger: logging.Logger = logging.getLogger(__name__)


def materialize_input(field: Field, **kwargs):
    """
    A widget for the materialize input field.
    """
    field_id = kwargs.pop("id", field.id)
    field_type = kwargs.get("type", "text")

    attributes = {
        "id": field_id,
        "name": field_id,
        "type": field_type,
        "class": "validate",
        "required": "",
    }

    if field.data is not None and kwargs.get("value", True):
        attributes["value"] = field.data

    if "data-length" in kwargs:
        attributes["data-length"] = kwargs["data-length"]

    grid = kwargs.get("grid", "")
    outer_params = {"class": f"input-field col {grid}"}

    label_params = {"for": field_id}

    # label = kwargs.get("label", field_id)
    label = field.label
    html = [f"<div {html_params(**outer_params)}>"]
    html.append(f"<input {html_params(**attributes)}></input>")
    html.append(f"<label {html_params(**label_params)}>{ label }</label>")
    if len(field.errors) > 0:
        error_text = ", ".join(field.errors)
        attributes = {"class": "red-text"}
        html.append(f"<span { html_params(**attributes) }>{ error_text }</span>")
    html.append("</div>")

    return "".join(html)


def materialize_submit(field, **kwargs):
    """
    A widget for the materialize submit button.
    """
    field_id = kwargs.pop("id", field.id)
    field_type = kwargs.get("type", "submit")
    label = field.label.text
    icon = kwargs.get("icon", "send")

    button_attrs = {
        "id": field_id,
        "type": field_type,
        "class": "btn blue waves-effect waves-light",
    }

    html = [f"<button {html_params(**button_attrs)}>{label}"]
    html.append(f"<i class='material-icons right'>{icon}</i>")
    html.append("</button>")
    return "".join(html)


class RegisterForm(FlaskForm):
    """
    The registration form
    """

    first_name = StringField("First Name", widget=materialize_input)
    last_name = StringField("Last Name", widget=materialize_input)
    email = StringField(
        "Email",
        widget=materialize_input,
        validators=[validators.Email(), validators.InputRequired()],
    )
    login = StringField(
        "Your Account Name", widget=materialize_input, validators=[validators.InputRequired()]
    )
    password = PasswordField(
        "Password", widget=materialize_input, validators=[validators.InputRequired()]
    )
    password2 = PasswordField(
        "Retype Password",
        widget=materialize_input,
        validators=[
            validators.InputRequired(),
            validators.EqualTo("password", message="Passwords are not identical."),
        ],
    )
    submit = SubmitField("Register", widget=materialize_submit)


class LoginForm(FlaskForm):
    """
    The login form.
    """

    login = StringField("Login", widget=materialize_input, validators=[validators.InputRequired()])
    password = PasswordField(
        "Password", widget=materialize_input, validators=[validators.InputRequired()]
    )
    submit = SubmitField("Login", widget=materialize_submit)
