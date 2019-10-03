"""
The Admin Blueprint
"""
import logging
from flask import Blueprint, render_template, abort, request

from digicubes.client import UserProxy
from digicubes.common.exceptions import DigiCubeError
from digicubes.common.structures import BearerTokenData
from digicubes.web.account import login_required, needs_right, account_manager
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
    """
        Logs current user out.
        Redirects to the configured unauthorized page.
    """
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
        try:
            user_login = form.login.data
            password = form.password.data
            account_manager.login(user_login, password)
            return account_manager.successful_logged_in()
        except DigiCubeError:
            return account_manager.unauthorized()

    logger.debug("Validation of the form failed")
    return render_template("root/login.jinja", form=form)


@account_service.route("/users/")
@login_required
def user_list():
    """The user list route."""
    return render_template("root/all_users.jinja")


@account_service.route("/panel/usertable/")
@login_required
def panel_user_table():
    """The user list route."""
    offset = request.args.get("offset", None)
    count = request.args.get("count", None)
    token = account_manager.token
    try:
        users = account_manager.user.all(token, offset=offset, count=count)
        return render_template("root/panel/user_table.jinja", users=users)
    except DigiCubeError:
        abort(500)


@account_service.route("/register", methods=["GET", "POST"])
def register():
    """
    Register a new user.
    """

    # You cannot register, if you are already logged in
    if account_manager.authenticated:
        return account_manager.successful_logged_in()

    form = RegisterForm()
    if form.validate_on_submit():

        try:
            # Need root rights for this
            # FIXME: don't put root credentials in code
            bearer_token: BearerTokenData = account_manager.generate_token_for("root", "digicubes")
            logger.debug("#" * 20)
            token = bearer_token.bearer_token
            logger.debug("#" * 20)

            autoverify = account_manager.auto_verify

            user = UserProxy(
                login=form.login.data,
                first_name=form.first_name.data,
                last_name=form.last_name.data,
                email=form.email.data,
                is_verified=autoverify,
                is_active=True,
            )
            # Create a new user in behalf of root
            user = account_manager.user.create(token, user)

            # Also setting the password in behalf of root
            account_manager.user.set_password(token, user.id, form.password.data)
            return account_manager.successful_logged_in()
        except DigiCubeError as e:
            logger.exception("Could not create new account.", exc_info=e)

    logger.debug("Validation of the form failed")
    return render_template("root/register.jinja", form=form)


@account_service.route("/right_test/")
@login_required
@needs_right("test_right")
def right_test():
    """
    This is just a test route to check, if the needs_right decorator works
    correctly.
    """
    return "YoLo"


@account_service.route("/roles/")
@needs_right("no_limits")
def roles():
    """
    Display all roles
    """
    return render_template("root/roles.jinja")
