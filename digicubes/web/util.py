"""
The main extension module
"""
import logging
from functools import wraps
from typing import Optional

from flask import (
    has_request_context,
    _request_ctx_stack,
    abort,
    current_app,
    request,
    Response,
    redirect,
    Flask,
    url_for,
    make_response
)
from flask_wtf.csrf import CSRFError
from werkzeug.local import LocalProxy

from .defaults import (
    TOKEN_COOKIE_NAME,
    DIGICUBES_ACCOUNT_INDEX_VIEW,
    DIGICUBES_ACCOUNT_LOGIN_VIEW,
    DIGICUBES_ACCOUNT_URL_PREFIX,
)

logger = logging.getLogger(__name__)

digi_client = LocalProxy(lambda: _get_client())
account_manager = LocalProxy(lambda: _get_account_manager())

DIGICUBES_ACCOUNT_ATTRIBUTE_NAME = "digicubes_account_manager"


def _get_account_manager():
    return getattr(current_app, DIGICUBES_ACCOUNT_ATTRIBUTE_NAME, None)


def _get_client():
    """
    Gets the ``FlaskDigiCubesClient`` from the current
    request context. If there is no client, the method
    creates a new client and stores it in the request
    context.
    """
    from .flask import FlaskDigiCubesClient

    if has_request_context() and not hasattr(
            _request_ctx_stack.top, DIGICUBES_ACCOUNT_ATTRIBUTE_NAME
        ):
        ctx = _request_ctx_stack.top
        app = ctx.app

        client = FlaskDigiCubesClient(
            protocol=app.config.get("DIGICUBES_API_SERVER_PROTOCOL", "http"),
            hostname=app.config.get("DIGICUBES_API_SERVER_HOSTNAME", "localhost"),
            port=app.config.get("DIGICUBES_API_SERVER_PORT", 3000),
        )
        setattr(ctx, DIGICUBES_ACCOUNT_ATTRIBUTE_NAME, client)

    # Return the client
    ctx = _request_ctx_stack.top
    client = getattr(ctx, DIGICUBES_ACCOUNT_ATTRIBUTE_NAME, None)
    return client


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
        token = account_manager.get_token()
        logger.debug("Looking up the token. Found %s", token)

        if token is not None and account_manager.token == token:
            # We have a token and it matches the current token
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

    def init_app(self, app: Flask) -> None:
        """
        Initialises the login manager and adds itself
        to the app.
        """
        from .blueprint import account_service

        if app is not None:
            app.digicubes_account_manager = self
            login_view = app.config.get(
                "DIGICUBES_ACCOUNT_LOGIN_VIEW", DIGICUBES_ACCOUNT_LOGIN_VIEW
            )
            index_view = app.config.get(
                "DIGICUBES_ACCOUNT_INDEX_VIEW", DIGICUBES_ACCOUNT_INDEX_VIEW
            )
            url_prefix = app.config.get(
                "DIGICUBES_ACCOUNT_URL_PREFIX", DIGICUBES_ACCOUNT_URL_PREFIX
            )
            self.unauthorized_callback = lambda: redirect(url_for(login_view))
            self.successful_logged_in_callback = lambda: redirect(url_for(index_view))
            app.register_blueprint(account_service, url_prefix=url_prefix)

            def update_token_cookie(response: Response):
                token = digi_client.token
                logger.debug("Setting token cookie %s", token)
                cookie_name = app.config.get("TOKEN_COOKIE_NAME", TOKEN_COOKIE_NAME)
                if token:
                    response.set_cookie(cookie_name, token)
                else:
                    response.set_cookie(cookie_name, "no-token", max_age=0)

                return response

            app.after_request(update_token_cookie)

            def find_token_in_request() -> Optional[str]:
                cookie_name = app.config.get("TOKEN_COOKIE_NAME", TOKEN_COOKIE_NAME)
                return request.cookies.get(cookie_name)

            def check_token():
                """
                Checks at the very beginning of every request, if we can
                find an authentification token in the request. If so, the
                token is stored in the digicubes client.
                """
                token = find_token_in_request()
                if token and digi_client:
                    digi_client.token = token

            app.before_request(check_token)
            app.context_processor(lambda: {"account_manager": account_manager})

            @app.errorhandler(CSRFError)
            def handle_csrf_error(e):
                #pylint: disable=unused-variable
                return e.description, 400

    @property
    def api(self):
        return digi_client

    def login(self, login, password):
        return self.api.login(login, password)

    def logout(self):
        self.api.logout()

    @property
    def token(self):
        return self.api.token

    @property
    def authenticated(self):
        # A bit crude the test.
        # Mayby a server call would be better,
        # as we do not know if it is a valid
        # token. But for the time being it
        # will do the job.
        return self.token is not None

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
        cookie_name = self._cfg.get("TOKEN_COOKIE_NAME", TOKEN_COOKIE_NAME)
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
