import logging
from functools import wraps

from flask import (
    has_request_context, _request_ctx_stack, abort, current_app
)
from werkzeug.local import LocalProxy

logger = logging.getLogger(__name__)

digi_client = LocalProxy(lambda: _get_client())

def _get_client():
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

    ctx = _request_ctx_stack.top
    client = getattr(ctx, "_digicubes_flask_client", None)
    return client

def login_required(f):
    """
    Decorator for route which should be only accessible for
    authorized user.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        client = digi_client
        app = current_app
        login_manager = app.digicubes_login_manager
        if client is None or not client.is_authorized:
            return login_manager.unauthorized()

        return f(*args, **kwargs)
    return decorated_function

class LoginManager:
    """
    Flask extension which is responsible for login and
    logout procedures.
    """
    def __init__(self, app=None):
        # Callbacks
        self.unauthorized_callback = None

        self.app = app
        self.init_app(app)

    def init_app(self, app):
        if app is not None:
            app.digicubes_login_manager = self

    def unauthorized_handler(self, callback):
        '''
        This will set the callback for the `unauthorized` method, which among
        other things is used by `login_required`. It takes no arguments, and
        should return a response to be sent to the user instead of their
        normal view.

        :param callback: The callback for unauthorized users.
        :type callback: callable
        '''
        self.unauthorized_callback = callback
        return callback

    def unauthorized(self):
        """
        Calls the unauthorized handel, or if no handler was
        set aborts with status 401.
        """
        if self.unauthorized_callback:
            return self.unauthorized_callback()

        # No handler set. Defaults to 401 error
        return abort(401)
