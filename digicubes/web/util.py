import logging
from functools import wraps
from typing import Optional

from flask import (
    has_request_context, _request_ctx_stack, abort, current_app, request, Response
)
from werkzeug.local import LocalProxy

from .contants import (
    TOKEN_COOKIE_NAME
)
logger = logging.getLogger(__name__)

digi_client = LocalProxy(lambda: _get_client())

def _get_client():
    """
    Gets the ``FlaskDigiCubesClient`` from the current
    request context. If there is no client, the method
    creates a new client and stores it in the request
    context.
    """
    from .flask import FlaskDigiCubesClient

    if has_request_context() and not hasattr(_request_ctx_stack.top, '_digicubes_flask_client'):
        ctx = _request_ctx_stack.top
        app = ctx.app

        client = FlaskDigiCubesClient(
            protocol=app.config.get('DIGICUBES_API_SERVER_PROTOCOL', 'http'),
            hostname=app.config.get('DIGICUBES_API_SERVER_HOSTNAME', 'localhost'),
            port=app.config.get('DIGICUBES_API_SERVER_PORT', 3000),
        )
        setattr(ctx, "_digicubes_flask_client", client)

    # Return the client
    ctx = _request_ctx_stack.top
    client = getattr(ctx, "_digicubes_flask_client", None)
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
        client = digi_client
        app = current_app
        login_manager = app.digicubes_login_manager

        # Check if we can find the token
        token = login_manager.get_token()
        logger.debug("Looking up the token. Found %s", token)

        if token is not None and client is not None and client.token == token:
            # We have a token and it matches the current token
            return f(*args, **kwargs)

        # Call the handler for unauthorized requests
        return login_manager.unauthorized()

    return decorated_function

class DigicubesAccountManager:
    """
    Flask extension which is responsible for login and
    logout procedures.
    """
    def __init__(self, app=None):
        # Callbacks
        self.unauthorized_callback = None
        self.successful_logged_in_callback = None

        self.app = app
        self.init_app(app)

    def init_app(self, app):
        """
        Initialises the login manager and adds itself
        to the app.
        """
        from .blueprints import admin, home
        
        if app is not None:
            app.digicubes_login_manager = self

            app.register_blueprint(admin, url_prefix="/admin")
            app.register_blueprint(home, url_prefix="/")

            @app.after_request
            def set_token_cookie(response: Response):
                token = digi_client.token
                if token and response:
                    cookie_name = app.config.get(TOKEN_COOKIE_NAME, 'digicubes.token')
                    logger.debug("Cookie name for the token (%s) is %s", token, cookie_name)
                    response.set_cookie(cookie_name, token)
                else:
                    logger.debug("No token. No Cookie.")
                return response

            def find_token_in_request() -> Optional[str]:
                return request.cookies.get('digicubes.token', None)
                    
            @app.before_request
            def check_token():
                token = find_token_in_request()
                if token and digi_client:
                    digi_client.token = token

            @app.context_processor
            def context():
                return {
                    "digi_client" : digi_client
                }


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
        cookie_name = self._cfg.get('TOKEN_COOKIE_NAME', TOKEN_COOKIE_NAME)
        return request.cookies.get(cookie_name, None)

    def _get_token_from_header(self):
        """
        lookup the token in the `Authorization` header of the request.
        The scheme has to be `Bearer`.
        """
        auth = request.headers.get('Authorization', None)
        if auth is not None:
            items = auth.strip().split(' ')
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
