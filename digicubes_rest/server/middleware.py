"""
Middleware classes to be added to the responder server.
"""
import logging

from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)


class SettingsMiddleware(BaseHTTPMiddleware):
    """
    Middleware to inject settings into the request state.
    This way all requests have access to the configuration
    values.
    """

    def __init__(self, app, settings, api=None):
        super().__init__(app)
        self.settings = settings
        self.api = api
        logger.info("Added settings middleware.")

    async def dispatch(self, request, call_next):
        """Adding the settings to the request state."""
        request.state.settings = self.settings
        if self.api is not None:
            request.state.api = self.api

        response = await call_next(request)
        return response