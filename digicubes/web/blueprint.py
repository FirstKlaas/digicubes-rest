"""
The Admin Blueprint
"""
from flask import Blueprint, render_template, abort

from .util import digi_client, login_required, account_manager
from .forms import LoginForm

account_service = Blueprint("account", __name__)


@account_service.route("/")
@login_required
def index():
    """The home route"""
    return render_template("root/base.jinja")


@account_service.route("/login", methods=["GET", "POST"])
def login():
    """
    Login route. On `GET`, it displays the login form.
    on `POST`, it tries to login to the account service.

    If authentification fails, it calls the `unauthorized`
    handler of the `DigicubesAccountManager`.

    If authentification was successful, it calls the
    `successful_logged_in` handler of the
    `DigicubesAccountManager`.
    """
    form = LoginForm()
    if form.validate_on_submit():
        login = form.login.data
        password = form.password.data
        token = digi_client.login(login, password)

        if account_manager is None:
            return abort(500)

        if token is None:
            return account_manager.unauthorized()

        return account_manager.successful_logged_in()

    return render_template("root/login.jinja", form=form)


@account_service.route("/users/")
def user_list():
    """The user list route."""
    return render_template("root/user_list.jinja")
