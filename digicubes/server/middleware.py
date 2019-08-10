import logging

from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)


class SettingsMiddleware(BaseHTTPMiddleware):
    """Middleware to inject settings into the request state"""

    def __init__(self, app, settings):
        super().__init__(app)
        self.settings = settings
        logger.info("Added settings middleware.")

    async def dispatch(self, request, call_next):
        request.state.settings = self.settings
        response = await call_next(request)
        return response
