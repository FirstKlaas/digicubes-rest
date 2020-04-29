"""
Middleware classes to be added to the responder server.
"""
import logging

from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)


class UpdateTokenMiddleware(BaseHTTPMiddleware):
    """
    This middleware component refreshes the authorization
    token during evry request and adds the new token
    to the header fields of the resonse.
    """

    def __init__(self, app, settings, api=None):
        super().__init__(app)
        self.settings = settings
        self.api = api
        logger.info("Added update token middleware.")

    async def dispatch(self, request, call_next):
        response = await call_next(request)
        # Now pimp the response
        auth_header = request.headers.get("authorization", None)
        if auth_header:
            # Check if the format is valid
            auth = auth_header.split(" ")
            if len(auth) == 2 and auth[0] == "Bearer":
                current_token = auth[1]
                digicubes_server = self.api.digicube
                info = digicubes_server.decodeBearerToken(current_token)
                new_token = digicubes_server.createBearerToken(info["user_id"])
                # storing the new token in the response
                response.headers["x-digicubes-token"] = new_token

        return response


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
