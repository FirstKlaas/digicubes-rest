"""
The Admin Blueprint
"""
import logging
from flask import Blueprint, render_template, abort, current_app

from digicubes.client import UserProxy
from digicubes.web.account import login_required, account_manager
from .forms import LoginForm, RegisterForm

account_service = Blueprint("account", __name__)

logger: logging.Logger = logging.getLogger(__name__)


@account_service.route("/")
@login_required
def index():
    """The home route"""
    return render_template("root/index.jinja")


@account_service.route("/logout", methods=["GET"])
@login_required
def logout():
    account_manager.logout()
    return account_manager.unauthorized()


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
    if account_manager is None:
        return abort(500)

    # If user is already authenticated, then
    # redirect him directly to the configured
    # starting page.
    if account_manager.authenticated:
        return account_manager.successful_logged_in()

    form = LoginForm()
    if form.validate_on_submit():

        user_login = form.login.data
        password = form.password.data
        token = account_manager.login(user_login, password)

        if token is None:
            return account_manager.unauthorized()

        return account_manager.successful_logged_in()

    logger.debug("Validation of the form failed")
    return render_template("root/login.jinja", form=form)


@account_service.route("/users/")
def user_list():
    """The user list route."""
    return render_template("root/user_list.jinja")


@account_service.route("/register", methods=["GET", "POST"])
def register():
    """
    Register a new user.
    """
    form = RegisterForm()
    if form.validate_on_submit():

        api = account_manager.api
        # Need root rights for this
        # FIXME: don't put root credentials in code 
        token = api.token_for('root', 'digicubes')
        autoverify = account_manager.auto_verify
        print('+'*40)
        print(autoverify)

        user = UserProxy(
            login=form.login.data,
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            email=form.email.data,
            is_verified=autoverify,
            is_active=True
        )
        # Create a new user in behalf of root
        user = api.user.create(user, token=token)

        # Also setting the password in behalf of root
        api.user.set_password(user.id, form.password.data, token=token)
        return account_manager.successful_logged_in()

    logger.debug("Validation of the form failed")
    return render_template("root/register.jinja", form=form)
