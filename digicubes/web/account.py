"""
The main extension module
"""
import logging
from functools import wraps
from typing import Optional

from flask import abort, current_app, request, Response, redirect, Flask, url_for, session
from flask_wtf.csrf import CSRFError
from werkzeug.local import LocalProxy

from digicubes.client import DigiCubeClient, RoleService, UserService
from digicubes.common.structures import BearerTokenData

logger = logging.getLogger(__name__)
# pylint: disable=unnecessary-lambda
account_manager = LocalProxy(lambda: _get_account_manager())
current_user = LocalProxy(lambda: _get_current_user())

DIGICUBES_ACCOUNT_ATTRIBUTE_NAME = "digicubes_account_manager"


class CurrentUser:

    __slots__ = ["token", "id"]

    def __init__(self, token=None, user_id=None):
        self.token = token
        self.id = user_id

    def __str__(self):
        return self.token

    def __eq__(self, other):
        return self.token == other

    def __ne__(self, value):
        return self.token != value

def _get_current_user():
    token = session.get("digicubes.account.token", None)
    user_id = session.get("digicubes.account.userid", None)
    return CurrentUser(token, user_id)


def _get_account_manager():
    return getattr(current_app, DIGICUBES_ACCOUNT_ATTRIBUTE_NAME, None)


def login_required(f):
    """
    Decorator for routes which should be only accessible for
    authorized user. The decorator tries to find the bearer
    token and if found checks if the token is equal to the
    one we have stored in the current api client.

    If no token can be found, or the tokens are not equal,
    the registered handler is called.
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):

        # Check if we can find the token
        token = current_user.token
        logger.debug("Looking up the token. Found %s", token)

        if token is not None:
            # We have a token
            return f(*args, **kwargs)

        # Call the handler for unauthorized requests
        return account_manager.unauthorized()

    return decorated_function


class DigicubesAccountManager:
    """
    Flask extension which is responsible for login and
    logout procedures.
    """

    def __init__(self, app=None):
        # Callbacks
        self.app = app
        self.init_app(app)
        self.unauthorized_callback = None
        self.successful_logged_in_callback = None

    def init_app(self, app: Flask) -> None:
        """
        Initialises the login manager and adds itself
        to the app.
        """
        from .modules.account import account_service, AccountConfig

        if app is not None:
            account_config = AccountConfig()
            app.config.from_object(account_config)
            app.digicubes_account_manager = self
            login_view = app.config.get(
                "DIGICUBES_ACCOUNT_LOGIN_VIEW", AccountConfig.DIGICUBES_ACCOUNT_LOGIN_VIEW
            )
            index_view = app.config.get(
                "DIGICUBES_ACCOUNT_INDEX_VIEW", AccountConfig.DIGICUBES_ACCOUNT_INDEX_VIEW
            )
            url_prefix = app.config.get(
                "DIGICUBES_ACCOUNT_URL_PREFIX", AccountConfig.DIGICUBES_ACCOUNT_URL_PREFIX
            )
            self.unauthorized_callback = lambda: redirect(url_for(login_view))
            self.successful_logged_in_callback = lambda: redirect(url_for(index_view))

            logger.debug("Register account blueprint at %s", url_prefix)
            app.register_blueprint(account_service, url_prefix=url_prefix)

            self._client = DigiCubeClient(
                protocol=app.config.get("DIGICUBES_API_SERVER_PROTOCOL", "http"),
                hostname=app.config.get("DIGICUBES_API_SERVER_HOSTNAME", "localhost"),
                port=app.config.get("DIGICUBES_API_SERVER_PORT", 3000),
            )

            def update_current_user(response: Response):
                user = current_user
                logger.debug("Setting token cookie %s", user.token)
                # Get the action (or None as default)
                action = session.get("digicubes.account.action", None)

                remember_token = user.token is not None and action != "logout"

                # This session value is no longer needed and there we
                # can savely remove it. Normally (the intended design)
                # this key, value pair shoul'd never be send to the
                # client.
                if "digicubes.account.action" in session:
                    session.pop("digicubes.account.action")

                if remember_token:
                    session["digicubes.account.token"] = user.token
                    session["digicubes.account.id"] = user.id
                else:
                    if "digicubes.account.token" in session:
                        session.pop("digicubes.account.token")

                    if "digicubes.account.id" in session:
                        session.pop("digicubes.account.id")

                return response

            # At the end of each request the session
            # variables are updated. The token as well as the session id 
            # are written to the session. Or removed if requested.
            app.after_request(update_current_user)

            app.context_processor(
                lambda: {"account_manager": account_manager, "current_user": current_user}
            )

            @app.errorhandler(CSRFError)
            def handle_csrf_error(e):
                # pylint: disable=unused-variable
                return e.description, 400

    @property
    def auto_verify(self):
        return current_app.config.get("DIGICUBES_ACCOUNT_AUTO_VERIFY", False)

    @property
    def token(self):
        return current_user.token

    @property
    def authenticated(self):
        # A bit crude the test.
        # Mayby a server call would be better,
        # as we do not know if it is a valid
        # token. But for the time being it
        # will do the job.
        return current_user.token is not None

    def successful_logged_in_handler(self, callback):
        """
        Setting the handler that is called, after a user
        has succesfully logged in. This callback is used by
        the `login` route.

        The callback must return the response, like any route.

        :param callback: The callback for successfully logged in users.
        :type callback: callable
        """
        self.successful_logged_in_callback = callback
        return callback

    def unauthorized_handler(self, callback):
        """
        This will set the callback for the `unauthorized` method, which among
        other things is used by `login_required`. It takes no arguments, and
        should return a response to be sent to the user instead of their
        normal view.

        :param callback: The callback for unauthorized users.
        :type callback: callable
        """
        self.unauthorized_callback = callback
        return callback

    def unauthorized(self):
        """
        Calls the unauthorized handler, or if no handler was
        set aborts with status 401.
        """
        if self.unauthorized_callback:
            return self.unauthorized_callback()

        # No handler set. Defaults to 401 error
        return abort(401)

    def successful_logged_in(self):
        """
        Calls the 'successful_logged_in` handler, or if no
        handler was registered aborts with status 404
        """
        if self.successful_logged_in_callback:
            return self.successful_logged_in_callback()
        return abort(404)

    @property
    def _cfg(self):
        app = current_app
        return app.config

    def _get_token_from_cookie(self):
        cookie_name = self._cfg.get("TOKEN_COOKIE_NAME", None)
        return request.cookies.get(cookie_name, None)

    def _get_token_from_header(self):
        """
        lookup the token in the `Authorization` header of the request.
        The scheme has to be `Bearer`.
        """
        auth = request.headers.get("Authorization", None)
        if auth is not None:
            items = auth.strip().split(" ")
            if len(items) == 2 and items[0].strip() == "Bearer":
                return items[1].strip()
        return None

    def get_token(self):
        """
        Tries to lookup the token from the cookie store and from
        the header. Returns `None` if the token couldn`t be found,
        the token else.
        """
        token = self._get_token_from_cookie()
        if token is None:
            token = self._get_token_from_header()
        return token

    def login(self, login: str, password: str) -> str:
        user: BearerTokenData = self._client.login(login, password)
        session["digicubes.account.token"] = user.bearer_token
        session["digicubes.account.id"] = user.user_id
        return user

    def generate_token_for(self, login: str, password: str) -> str:
        return self._client.generate_token_for(login, password)

    def logout(self):
        session["digicubes.account.action"] = "logout"

    @property
    def user(self) -> UserService:
        """user servives"""
        return self._client.user_service

    @property
    def role(self) -> RoleService:
        """role services"""
        return self._client.role_service
